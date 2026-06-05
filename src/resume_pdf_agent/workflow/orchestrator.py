"""M10 deterministic workflow orchestrator.

Connects M0–M9 modules into a single end-to-end function that can be called
programmatically or via CLI.
"""

from __future__ import annotations

from pathlib import Path

from resume_pdf_agent.classifier import classify_resume_type
from resume_pdf_agent.confirmation import (
    apply_confirmation_decisions,
    build_confirmation_gate_warning,
    build_confirmation_packet,
    load_confirmation_decisions,
    render_confirmation_review_markdown,
    should_block_final_pdf,
)
from resume_pdf_agent.criteria import load_criteria_profile, select_criteria_profiles
from resume_pdf_agent.enhancement import enhance_resume_bullets
from resume_pdf_agent.gap_analysis import analyze_criteria_gap
from resume_pdf_agent.models.pdf import PDFBackend, PDFGenerationOptions
from resume_pdf_agent.models.rendering import HTMLRenderOptions
from resume_pdf_agent.models.workflow import (
    ResumeWorkflowInput,
    ResumeWorkflowResult,
    WorkflowArtifact,
    WorkflowRunStatus,
    WorkflowStageName,
    WorkflowStageResult,
    WorkflowStageStatus,
)
from resume_pdf_agent.pdf import generate_pdf_from_html_result
from resume_pdf_agent.pdf.options import build_conversion_reminder
from resume_pdf_agent.rendering import render_resume_html, write_rendered_html
from resume_pdf_agent.templates import select_internal_template
from resume_pdf_agent.truthfulness import check_truthfulness
from resume_pdf_agent.workflow.io import ensure_output_dir
from resume_pdf_agent.workflow.serialization import write_json_artifact


def _stage_result(
    stage: WorkflowStageName,
    status: WorkflowStageStatus,
    message: str,
    warnings: list[str] | None = None,
    errors: list[str] | None = None,
    artifacts: list[WorkflowArtifact] | None = None,
) -> WorkflowStageResult:
    return WorkflowStageResult(
        stage=stage,
        status=status,
        message=message,
        warnings=warnings or [],
        errors=errors or [],
        artifacts=artifacts or [],
    )


def _json_path(output_dir: Path, filename: str) -> Path:
    return output_dir / filename


def _artifact_filename(artifact_type: str, ext: str) -> str:
    return f"{artifact_type}.{ext}"


def run_resume_workflow(
    workflow_input: ResumeWorkflowInput,
) -> ResumeWorkflowResult:
    """Execute the deterministic end-to-end resume workflow.

    Stages
    ------
    1. User intake (setup)
    2. Criteria selection
    3. Resume type classification
    4. Gap analysis
    5. Truthfulness check
    6. Criteria-aware content enhancement
    7. Internal template matching
    8. HTML rendering
    9. PDF generation
    10. Artifact collection
    11. Reminder panel (metadata only)
    """

    output_dir = ensure_output_dir(workflow_input.output_dir)
    stages: list[WorkflowStageResult] = []
    all_artifacts: list[WorkflowArtifact] = []
    global_warnings: list[str] = []
    global_errors: list[str] = []

    selected_criteria_profile_id: str | None = None
    primary_resume_type = None
    selected_template_id: str | None = None
    html_output_path: str | None = None
    pdf_output_path: str | None = None
    conversion_reminder: str | None = None
    # M14 confirmation
    confirmation_packet_path: str | None = None
    confirmation_review_path: str | None = None
    confirmation_required: bool = False
    can_generate_final_pdf: bool = True

    # ── A. User intake (setup) ─────────────────────────────────────────────
    stages.append(
        _stage_result(
            WorkflowStageName.USER_INTAKE,
            WorkflowStageStatus.COMPLETED,
            f"Workflow input validated; output directory: {output_dir}",
        )
    )

    # ── B. Criteria selection ──────────────────────────────────────────────
    try:
        if workflow_input.criteria_profile_id:
            criteria_profile = load_criteria_profile(workflow_input.criteria_profile_id)
            selected_criteria_profile_id = workflow_input.criteria_profile_id
        else:
            target_role = workflow_input.target_role or (
                workflow_input.user_profile.target_roles[0]
                if workflow_input.user_profile.target_roles
                else None
            )
            profiles = select_criteria_profiles(target_role=target_role)
            if not profiles:
                raise RuntimeError(
                    f"No criteria profile could be selected for target_role={target_role!r}"
                )
            criteria_profile = profiles[0]
            selected_criteria_profile_id = criteria_profile.profile_id

        stages.append(
            _stage_result(
                WorkflowStageName.CRITERIA_SELECTION,
                WorkflowStageStatus.COMPLETED,
                f"Selected criteria profile: {selected_criteria_profile_id}",
            )
        )

        if workflow_input.write_intermediate_json:
            art = write_json_artifact(
                criteria_profile,
                _json_path(output_dir, _artifact_filename("criteria_profile", "json")),
            )
            all_artifacts.append(art)
    except Exception as exc:
        stages.append(
            _stage_result(
                WorkflowStageName.CRITERIA_SELECTION,
                WorkflowStageStatus.FAILED,
                f"Criteria selection failed: {exc}",
                errors=[str(exc)],
            )
        )
        global_errors.append(str(exc))
        # cannot continue without criteria
        return _build_result(
            output_dir, stages, all_artifacts, global_warnings, global_errors,
            selected_criteria_profile_id, primary_resume_type,
            selected_template_id, html_output_path, pdf_output_path,
            conversion_reminder,
        )

    # ── C. Resume type classification ──────────────────────────────────────
    try:
        classification_result = classify_resume_type(
            user_profile=workflow_input.user_profile,
            resume_content=workflow_input.resume_content,
            criteria_profiles=[criteria_profile],
        )
        primary_resume_type = classification_result.primary_resume_type

        stage_status = WorkflowStageStatus.COMPLETED
        stage_warnings: list[str] = list(classification_result.warnings)
        if stage_warnings:
            stage_status = WorkflowStageStatus.COMPLETED_WITH_WARNINGS
            global_warnings.extend(stage_warnings)

        stages.append(
            _stage_result(
                WorkflowStageName.RESUME_TYPE_CLASSIFICATION,
                stage_status,
                f"Classified as {primary_resume_type.value} (confidence: {classification_result.confidence:.2f})",
                warnings=stage_warnings,
            )
        )

        if workflow_input.write_intermediate_json:
            art = write_json_artifact(
                classification_result,
                _json_path(output_dir, _artifact_filename("classification", "json")),
            )
            all_artifacts.append(art)
    except Exception as exc:
        stages.append(
            _stage_result(
                WorkflowStageName.RESUME_TYPE_CLASSIFICATION,
                WorkflowStageStatus.FAILED,
                f"Classification failed: {exc}",
                errors=[str(exc)],
            )
        )
        global_errors.append(str(exc))
        return _build_result(
            output_dir, stages, all_artifacts, global_warnings, global_errors,
            selected_criteria_profile_id, primary_resume_type,
            selected_template_id, html_output_path, pdf_output_path,
            conversion_reminder,
        )

    # ── D. Gap analysis ────────────────────────────────────────────────────
    try:
        gap_result = analyze_criteria_gap(
            user_profile=workflow_input.user_profile,
            criteria_profile=criteria_profile,
            resume_content=workflow_input.resume_content,
            classification_result=classification_result,
        )

        stage_status = WorkflowStageStatus.COMPLETED
        gap_warnings: list[str] = list(gap_result.truthfulness_warnings)
        if gap_warnings:
            stage_status = WorkflowStageStatus.COMPLETED_WITH_WARNINGS
            global_warnings.extend(gap_warnings)

        stages.append(
            _stage_result(
                WorkflowStageName.GAP_ANALYSIS,
                stage_status,
                f"Gap analysis complete; overall match: {gap_result.overall_match_level.value}",
                warnings=gap_warnings,
            )
        )

        if workflow_input.write_intermediate_json:
            art = write_json_artifact(
                gap_result,
                _json_path(output_dir, _artifact_filename("gap_analysis", "json")),
            )
            all_artifacts.append(art)
    except Exception as exc:
        stages.append(
            _stage_result(
                WorkflowStageName.GAP_ANALYSIS,
                WorkflowStageStatus.FAILED,
                f"Gap analysis failed: {exc}",
                errors=[str(exc)],
            )
        )
        global_errors.append(str(exc))
        return _build_result(
            output_dir, stages, all_artifacts, global_warnings, global_errors,
            selected_criteria_profile_id, primary_resume_type,
            selected_template_id, html_output_path, pdf_output_path,
            conversion_reminder,
        )

    # ── E. Truthfulness check ──────────────────────────────────────────────
    try:
        truthfulness_result = check_truthfulness(
            resume_content=workflow_input.resume_content,
            gap_analysis_result=gap_result,
        )

        stage_status = WorkflowStageStatus.COMPLETED
        truth_warnings: list[str] = list(truthfulness_result.warnings)
        if truth_warnings:
            stage_status = WorkflowStageStatus.COMPLETED_WITH_WARNINGS
            global_warnings.extend(truth_warnings)

        stages.append(
            _stage_result(
                WorkflowStageName.TRUTHFULNESS_CHECK,
                stage_status,
                f"Truthfulness check complete; risk: {truthfulness_result.overall_risk_level.value}; "
                f"claims checked: {truthfulness_result.claims_checked}; "
                f"safe to proceed: {truthfulness_result.safe_to_proceed}",
                warnings=truth_warnings,
            )
        )

        if workflow_input.write_intermediate_json:
            art = write_json_artifact(
                truthfulness_result,
                _json_path(output_dir, _artifact_filename("truthfulness", "json")),
            )
            all_artifacts.append(art)
    except Exception as exc:
        stages.append(
            _stage_result(
                WorkflowStageName.TRUTHFULNESS_CHECK,
                WorkflowStageStatus.FAILED,
                f"Truthfulness check failed: {exc}",
                errors=[str(exc)],
            )
        )
        global_errors.append(str(exc))
        return _build_result(
            output_dir, stages, all_artifacts, global_warnings, global_errors,
            selected_criteria_profile_id, primary_resume_type,
            selected_template_id, html_output_path, pdf_output_path,
            conversion_reminder,
        )

    # ── F. Criteria-aware content enhancement ──────────────────────────────
    try:
        enhancement_result = enhance_resume_bullets(
            resume_content=workflow_input.resume_content,
            criteria_profile=criteria_profile,
            gap_analysis_result=gap_result,
            truthfulness_result=truthfulness_result,
        )

        stage_status = WorkflowStageStatus.COMPLETED
        enh_warnings: list[str] = (
            list(enhancement_result.global_warnings)
            + list(enhancement_result.truthfulness_blockers)
        )
        if enh_warnings:
            stage_status = WorkflowStageStatus.COMPLETED_WITH_WARNINGS
            global_warnings.extend(enh_warnings)

        stages.append(
            _stage_result(
                WorkflowStageName.CRITERIA_AWARE_CONTENT_ENHANCEMENT,
                stage_status,
                f"Enhancement complete; candidates: {enhancement_result.candidates_generated}; "
                f"safe: {enhancement_result.safe_candidates_count}; "
                f"need confirmation: {enhancement_result.candidates_requiring_confirmation}",
                warnings=enh_warnings,
            )
        )

        if workflow_input.write_intermediate_json:
            art = write_json_artifact(
                enhancement_result,
                _json_path(output_dir, _artifact_filename("enhancement", "json")),
            )
            all_artifacts.append(art)
    except Exception as exc:
        stages.append(
            _stage_result(
                WorkflowStageName.CRITERIA_AWARE_CONTENT_ENHANCEMENT,
                WorkflowStageStatus.FAILED,
                f"Enhancement failed: {exc}",
                errors=[str(exc)],
            )
        )
        global_errors.append(str(exc))
        return _build_result(
            output_dir, stages, all_artifacts, global_warnings, global_errors,
            selected_criteria_profile_id, primary_resume_type,
            selected_template_id, html_output_path, pdf_output_path,
            conversion_reminder,
        )

    # ── G. Internal template matching ──────────────────────────────────────
    try:
        template_result = select_internal_template(
            user_profile=workflow_input.user_profile,
            resume_content=workflow_input.resume_content,
            classification_result=classification_result,
            criteria_profile=criteria_profile,
            gap_analysis_result=gap_result,
            bullet_enhancement_result=enhancement_result,
        )
        selected_template_id = template_result.selected_template_id

        stage_status = WorkflowStageStatus.COMPLETED
        tmpl_warnings: list[str] = list(template_result.warnings)
        if tmpl_warnings:
            stage_status = WorkflowStageStatus.COMPLETED_WITH_WARNINGS
            global_warnings.extend(tmpl_warnings)

        stages.append(
            _stage_result(
                WorkflowStageName.INTERNAL_TEMPLATE_MATCHING,
                stage_status,
                f"Selected template: {selected_template_id}",
                warnings=tmpl_warnings,
            )
        )

        if workflow_input.write_intermediate_json:
            art = write_json_artifact(
                template_result,
                _json_path(output_dir, _artifact_filename("template_selection", "json")),
            )
            all_artifacts.append(art)
    except Exception as exc:
        stages.append(
            _stage_result(
                WorkflowStageName.INTERNAL_TEMPLATE_MATCHING,
                WorkflowStageStatus.FAILED,
                f"Template matching failed: {exc}",
                errors=[str(exc)],
            )
        )
        global_errors.append(str(exc))
        return _build_result(
            output_dir, stages, all_artifacts, global_warnings, global_errors,
            selected_criteria_profile_id, primary_resume_type,
            selected_template_id, html_output_path, pdf_output_path,
            conversion_reminder,
        )

    # ── H. HTML rendering ──────────────────────────────────────────────────
    try:
        html_options = HTMLRenderOptions(
            include_preview_reminder_panel=workflow_input.include_preview_reminder_panel,
        )
        html_result = render_resume_html(
            user_profile=workflow_input.user_profile,
            resume_content=workflow_input.resume_content,
            template_selection_result=template_result,
            bullet_enhancement_result=enhancement_result,
            options=html_options,
        )
        html_result = write_rendered_html(
            html_result,
            output_dir / "resume.html",
        )
        html_output_path = str(output_dir / "resume.html")

        stage_status = WorkflowStageStatus.COMPLETED
        html_warnings: list[str] = list(html_result.warnings)
        if html_warnings:
            stage_status = WorkflowStageStatus.COMPLETED_WITH_WARNINGS
            global_warnings.extend(html_warnings)

        stages.append(
            _stage_result(
                WorkflowStageName.HTML_RENDERING,
                stage_status,
                f"HTML rendered to {html_output_path}",
                warnings=html_warnings,
                artifacts=[
                    WorkflowArtifact(
                        artifact_type="html",
                        path=html_output_path,
                        description="Rendered resume HTML",
                    )
                ],
            )
        )
        if html_output_path:
            all_artifacts.append(
                WorkflowArtifact(
                    artifact_type="html",
                    path=html_output_path,
                    description="Rendered resume HTML",
                )
            )
    except Exception as exc:
        stages.append(
            _stage_result(
                WorkflowStageName.HTML_RENDERING,
                WorkflowStageStatus.FAILED,
                f"HTML rendering failed: {exc}",
                errors=[str(exc)],
            )
        )
        global_errors.append(str(exc))
        return _build_result(
            output_dir, stages, all_artifacts, global_warnings, global_errors,
            selected_criteria_profile_id, primary_resume_type,
            selected_template_id, html_output_path, pdf_output_path,
            conversion_reminder,
        )

    # ── H5. Confirmation review (M14) ──────────────────────────────────
    try:
        if workflow_input.write_confirmation_packet:
            packet = build_confirmation_packet(
                resume_content=workflow_input.resume_content,
                truthfulness_result=truthfulness_result,
                bullet_enhancement_result=enhancement_result,
                gap_analysis_result=gap_result,
            )

            # Load and apply decisions if provided
            review_result = None
            if workflow_input.confirmation_decisions_path:
                try:
                    decision_set = load_confirmation_decisions(
                        workflow_input.confirmation_decisions_path
                    )
                    review_result = apply_confirmation_decisions(packet, decision_set)
                    can_generate_final_pdf = review_result.can_generate_final_pdf
                except Exception as dec_exc:
                    global_warnings.append(
                        f"Failed to apply confirmation decisions: {dec_exc}"
                    )
                    can_generate_final_pdf = packet.can_generate_final_pdf
            else:
                can_generate_final_pdf = packet.can_generate_final_pdf

            # Write confirmation packet JSON (only if intermediate JSON enabled)
            if workflow_input.write_intermediate_json:
                pkt_art = write_json_artifact(
                    packet,
                    _json_path(output_dir, _artifact_filename("confirmation_packet", "json")),
                )
                all_artifacts.append(pkt_art)
                confirmation_packet_path = pkt_art.path
            else:
                confirmation_packet_path = None

            # Write confirmation review markdown
            review_md = render_confirmation_review_markdown(packet, review_result)
            review_md_path = output_dir / "confirmation_review.md"
            review_md_path.write_text(review_md, encoding="utf-8")
            confirmation_review_path = str(review_md_path)
            all_artifacts.append(
                WorkflowArtifact(
                    artifact_type="confirmation_review",
                    path=str(review_md_path),
                    description="User confirmation review document (Chinese)",
                )
            )

            # Write review result if decisions were applied
            if review_result is not None and workflow_input.write_intermediate_json:
                rr_art = write_json_artifact(
                    review_result,
                    _json_path(
                        output_dir,
                        _artifact_filename("confirmation_review_result", "json"),
                    ),
                )
                all_artifacts.append(rr_art)

            # Determine if confirmation is required (gate check)
            if workflow_input.require_confirmation_before_pdf:
                if should_block_final_pdf(packet):
                    confirmation_required = True
                    can_generate_final_pdf = False
                    gate_warning = build_confirmation_gate_warning(packet)
                    if gate_warning:
                        global_warnings.append(gate_warning)

            conf_stage_status = WorkflowStageStatus.COMPLETED
            conf_warnings: list[str] = list(packet.warnings)
            if confirmation_required:
                conf_stage_status = WorkflowStageStatus.COMPLETED_WITH_WARNINGS

            stages.append(
                _stage_result(
                    WorkflowStageName.CONFIRMATION_REVIEW,
                    conf_stage_status,
                    (
                        f"Confirmation packet: {len(packet.items)} items; "
                        f"blocking: {packet.blocking_count}; "
                        f"can generate PDF: {can_generate_final_pdf}"
                    ),
                    warnings=conf_warnings,
                )
            )
    except Exception as exc:
        stages.append(
            _stage_result(
                WorkflowStageName.CONFIRMATION_REVIEW,
                WorkflowStageStatus.FAILED,
                f"Confirmation review failed: {exc}",
                errors=[str(exc)],
            )
        )
        global_errors.append(str(exc))

    # ── I. PDF generation ──────────────────────────────────────────────────
    # M14: Skip PDF if confirmation gate blocks
    if workflow_input.require_confirmation_before_pdf and not can_generate_final_pdf:
        stages.append(
            _stage_result(
                WorkflowStageName.PDF_GENERATION,
                WorkflowStageStatus.SKIPPED,
                (
                    "PDF generation skipped: user confirmation required before final PDF. "
                    "Review confirmation_packet.json and provide decisions via "
                    "--confirmation-decisions."
                ),
                warnings=[
                    (
                        "PDF skipped due to confirmation gate. "
                        "Resolve blocking confirmation items and re-run."
                    )
                ],
            )
        )
        pdf_output_path = None
    else:
        try:
            pdf_options = PDFGenerationOptions(
                backend=workflow_input.pdf_backend,
                include_conversion_reminder=True,
            )
            pdf_result = generate_pdf_from_html_result(
                html_render_result=html_result,
                output_path=output_dir / "resume.pdf",
                options=pdf_options,
            )

            if pdf_result.output_path:
                pdf_output_path = pdf_result.output_path

            pdf_warnings: list[str] = list(pdf_result.warnings)
            pdf_errors: list[str] = list(pdf_result.errors)

            conversion_reminder = pdf_result.conversion_reminder

            if pdf_errors:
                pdf_stage_status = WorkflowStageStatus.FAILED
                global_errors.extend(pdf_errors)
            elif pdf_warnings:
                pdf_stage_status = WorkflowStageStatus.COMPLETED_WITH_WARNINGS
                global_warnings.extend(pdf_warnings)
            else:
                pdf_stage_status = WorkflowStageStatus.COMPLETED

            pdf_msg = f"PDF generated to {pdf_output_path}" if pdf_output_path else "PDF not generated"
            stages.append(
                _stage_result(
                    WorkflowStageName.PDF_GENERATION,
                    pdf_stage_status,
                    pdf_msg,
                    warnings=pdf_warnings,
                    errors=pdf_errors,
                    artifacts=(
                        [
                            WorkflowArtifact(
                                artifact_type="pdf",
                                path=pdf_output_path,
                                description="Generated resume PDF",
                            )
                        ]
                        if pdf_output_path
                        else []
                    ),
                )
            )
            if pdf_output_path:
                all_artifacts.append(
                    WorkflowArtifact(
                        artifact_type="pdf",
                        path=pdf_output_path,
                        description="Generated resume PDF",
                    )
                )
        except Exception as exc:
            stages.append(
                _stage_result(
                    WorkflowStageName.PDF_GENERATION,
                    WorkflowStageStatus.FAILED,
                    f"PDF generation failed: {exc}",
                    errors=[str(exc)],
                )
            )
            global_errors.append(str(exc))

    # ── J. Artifact writing ────────────────────────────────────────────────
    stages.append(
        _stage_result(
            WorkflowStageName.ARTIFACT_WRITING,
            WorkflowStageStatus.COMPLETED,
            f"Collected {len(all_artifacts)} artifacts in {output_dir}",
            artifacts=all_artifacts,
        )
    )

    # ── K. Reminder panel (metadata only, not in resume body) ──────────────
    reminder = build_conversion_reminder(include=True)
    stages.append(
        _stage_result(
            WorkflowStageName.REMINDER_PANEL,
            WorkflowStageStatus.COMPLETED,
            "Conversion reminder added as metadata (not in resume body).",
            warnings=([reminder] if reminder else []),
        )
    )

    result = _build_result(
        output_dir, stages, all_artifacts, global_warnings, global_errors,
        selected_criteria_profile_id, primary_resume_type,
        selected_template_id, html_output_path, pdf_output_path,
        conversion_reminder,
        confirmation_packet_path=confirmation_packet_path,
        confirmation_review_path=confirmation_review_path,
        confirmation_required=confirmation_required,
        can_generate_final_pdf=can_generate_final_pdf,
    )

    # ── L. Write workflow_result.json if intermediate JSON is enabled ──────
    if workflow_input.write_intermediate_json:
        try:
            wf_json_art = write_json_artifact(
                result,
                _json_path(output_dir, _artifact_filename("workflow_result", "json")),
            )
            # Add to result artifacts and stage
            all_artifacts.append(wf_json_art)
            result.artifacts.append(wf_json_art)
        except Exception:
            # Non-fatal; do not fail the workflow over result serialization
            pass

    return result


def _build_result(
    output_dir: Path,
    stages: list[WorkflowStageResult],
    all_artifacts: list[WorkflowArtifact],
    global_warnings: list[str],
    global_errors: list[str],
    selected_criteria_profile_id: str | None,
    primary_resume_type,
    selected_template_id: str | None,
    html_output_path: str | None,
    pdf_output_path: str | None,
    conversion_reminder: str | None,
    confirmation_packet_path: str | None = None,
    confirmation_review_path: str | None = None,
    confirmation_required: bool = False,
    can_generate_final_pdf: bool = True,
) -> ResumeWorkflowResult:
    """Assemble the final ResumeWorkflowResult."""

    if global_errors:
        status = WorkflowRunStatus.FAILED
    elif global_warnings:
        status = WorkflowRunStatus.COMPLETED_WITH_WARNINGS
    else:
        status = WorkflowRunStatus.COMPLETED

    stage_descriptions = ", ".join(
        f"{s.stage.value}={s.status.value}" for s in stages
    )
    summary = (
        f"Workflow {status.value}. "
        f"Stages: [{stage_descriptions}]. "
        f"Output: {output_dir}. "
        f"Criteria: {selected_criteria_profile_id or 'N/A'}. "
        f"Type: {primary_resume_type.value if primary_resume_type else 'N/A'}. "
        f"Template: {selected_template_id or 'N/A'}. "
        f"HTML: {html_output_path or 'N/A'}. "
        f"PDF: {pdf_output_path or 'N/A'}."
    )

    return ResumeWorkflowResult(
        status=status,
        output_dir=str(output_dir),
        stages=stages,
        artifacts=all_artifacts,
        selected_criteria_profile_id=selected_criteria_profile_id,
        primary_resume_type=primary_resume_type,
        selected_template_id=selected_template_id,
        html_output_path=html_output_path,
        pdf_output_path=pdf_output_path,
        warnings=global_warnings,
        errors=global_errors,
        conversion_reminder=conversion_reminder,
        summary=summary,
        confirmation_packet_path=confirmation_packet_path,
        confirmation_review_path=confirmation_review_path,
        confirmation_required=confirmation_required,
        can_generate_final_pdf=can_generate_final_pdf,
    )
