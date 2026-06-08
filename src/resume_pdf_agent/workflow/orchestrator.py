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
    # M15 JD
    parsed_jd_path: str | None = None
    jd_criteria_profile_path: str | None = None
    jd_compliance_status: str | None = None
    used_user_provided_jd: bool = False
    # M16 LLM
    llm_rewrite_result_path: str | None = None
    llm_rewriting_used: bool = False
    # M20 confirmation UI
    confirmation_ui_path: str | None = None
    # M22 LLM review UI
    llm_review_ui_path: str | None = None
    # M23 LLM review decision summary
    llm_review_decision_summary_json_path: str | None = None
    llm_review_decision_summary_md_path: str | None = None
    # M24 LLM application plan
    llm_application_plan_json_path: str | None = None
    llm_application_plan_md_path: str | None = None
    # M25 LLM application preview UI
    llm_application_preview_ui_path: str | None = None
    # M26 pre-application validation
    llm_pre_application_validation_json_path: str | None = None
    llm_pre_application_validation_md_path: str | None = None
    # M27 manual patch preview
    llm_manual_patch_preview_json_path: str | None = None
    llm_manual_patch_preview_md_path: str | None = None
    llm_manual_patch_preview_html_path: str | None = None

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
        # M15: Use user-provided JD if enabled
        if workflow_input.use_user_provided_jd:
            used_user_provided_jd = True

            # Load JD text
            jd_text: str | None = None
            if workflow_input.jd_file_path:
                from resume_pdf_agent.jd.io import load_jd_text_from_file
                jd_text = load_jd_text_from_file(workflow_input.jd_file_path)
            elif workflow_input.jd_text:
                jd_text = workflow_input.jd_text

            if jd_text:
                from resume_pdf_agent.jd import (
                    build_criteria_profile_from_jd,
                    parse_user_provided_jd,
                )
                from resume_pdf_agent.jd.io import (
                    write_jd_criteria_artifact,
                    write_parsed_jd_artifact,
                )

                parsed = parse_user_provided_jd(jd_text)
                jd_compliance_status = parsed.compliance_result.status.value

                # Write parsed JD artifact
                if workflow_input.write_jd_artifacts and workflow_input.write_intermediate_json:
                    pjd_art = write_parsed_jd_artifact(
                        parsed,
                        _json_path(output_dir, _artifact_filename("parsed_jd", "json")),
                    )
                    all_artifacts.append(pjd_art)
                    parsed_jd_path = pjd_art.path

                # Build criteria from JD
                if parsed.compliance_result.can_parse:
                    jd_build = build_criteria_profile_from_jd(parsed)
                    if jd_build.criteria_profile is not None:
                        criteria_profile = jd_build.criteria_profile
                        selected_criteria_profile_id = criteria_profile.profile_id

                        if workflow_input.write_jd_artifacts and workflow_input.write_intermediate_json:
                            jdc_art = write_jd_criteria_artifact(
                                jd_build,
                                _json_path(
                                    output_dir,
                                    _artifact_filename("jd_criteria_profile", "json"),
                                ),
                            )
                            if jdc_art:
                                all_artifacts.append(jdc_art)
                                jd_criteria_profile_path = jdc_art.path
                    else:
                        global_warnings.append(
                            f"JD criteria build failed: {'; '.join(jd_build.errors)}"
                        )
                else:
                    global_warnings.append(
                        f"JD compliance blocked: {parsed.compliance_result.summary}"
                    )
                    # Fall back to static criteria
                    target_role = workflow_input.target_role or (
                        workflow_input.user_profile.target_roles[0]
                        if workflow_input.user_profile.target_roles
                        else None
                    )
                    profiles = select_criteria_profiles(target_role=target_role)
                    if profiles:
                        criteria_profile = profiles[0]
                        selected_criteria_profile_id = criteria_profile.profile_id
                        used_user_provided_jd = False
                    else:
                        raise RuntimeError("No criteria profile available (JD blocked, no static fallback).")
            else:
                global_warnings.append("use_user_provided_jd is true but no JD text or file provided.")
                used_user_provided_jd = False

        if not used_user_provided_jd:
            # Existing static criteria selection
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

    # ── H5b. Confirmation UI render (M20) ──────────────────────────────
    if workflow_input.write_confirmation_ui and confirmation_packet_path:
        try:
            from resume_pdf_agent.confirmation_ui import render_confirmation_ui_page

            # Rebuild packet (or load from file)
            packet = build_confirmation_packet(
                resume_content=workflow_input.resume_content,
                truthfulness_result=truthfulness_result,
                bullet_enhancement_result=enhancement_result,
                gap_analysis_result=gap_result,
            )

            ui_path = output_dir / "confirmation.html"
            ui_result = render_confirmation_ui_page(packet, ui_path)
            if ui_result.output_path:
                confirmation_ui_path = str(ui_result.output_path)
                all_artifacts.append(
                    WorkflowArtifact(
                        artifact_type="confirmation_ui",
                        path=str(ui_result.output_path),
                        description="Browser confirmation review page (static HTML)",
                    )
                )
        except Exception as exc:
            global_warnings.append(f"Confirmation UI render failed: {exc}")

    # ── H6. LLM-assisted rewrite (M16) ──────────────────────────────────
    try:
        if workflow_input.enable_llm_rewriting:
            from resume_pdf_agent.llm import rewrite_bullets_with_llm
            from resume_pdf_agent.llm.config import default_llm_rewrite_options
            from resume_pdf_agent.models.llm import LLMProviderType

            llm_opts = default_llm_rewrite_options()
            llm_opts.enabled = True

            # Determine provider
            provider_str = (workflow_input.llm_provider or "mock").lower()
            if provider_str == "mock":
                llm_opts.provider = LLMProviderType.MOCK
            elif provider_str == "external":
                llm_opts.provider = LLMProviderType.EXTERNAL
            else:
                llm_opts.provider = LLMProviderType.DISABLED

            # Build confirmation packet for safety gate
            cfm_packet = None
            try:
                cfm_packet = build_confirmation_packet(
                    resume_content=workflow_input.resume_content,
                    truthfulness_result=truthfulness_result,
                    bullet_enhancement_result=enhancement_result,
                    gap_analysis_result=gap_result,
                )
            except Exception:
                pass

            llm_result = rewrite_bullets_with_llm(
                resume_content=workflow_input.resume_content,
                bullet_enhancement_result=enhancement_result,
                truthfulness_result=truthfulness_result,
                confirmation_packet=cfm_packet,
                criteria_profile=criteria_profile,
                options=llm_opts,
            )

            llm_rewriting_used = True

            # Write LLM artifact
            if workflow_input.write_llm_artifacts and workflow_input.write_intermediate_json:
                lr_art = write_json_artifact(
                    llm_result,
                    _json_path(output_dir, _artifact_filename("llm_rewrite_result", "json")),
                )
                all_artifacts.append(lr_art)
                llm_rewrite_result_path = lr_art.path

            # Add warnings
            if llm_result.warnings:
                global_warnings.extend(llm_result.warnings)

            stages.append(
                _stage_result(
                    WorkflowStageName.CRITERIA_AWARE_CONTENT_ENHANCEMENT,
                    WorkflowStageStatus.COMPLETED,
                    f"LLM rewrite: {llm_result.candidates_generated} candidates; "
                    f"status: {llm_result.status.value}; "
                    f"provider: {llm_result.provider.value}",
                    warnings=list(llm_result.warnings),
                )
            )
    except Exception as exc:
        stages.append(
            _stage_result(
                WorkflowStageName.CRITERIA_AWARE_CONTENT_ENHANCEMENT,
                WorkflowStageStatus.COMPLETED_WITH_WARNINGS,
                f"LLM rewrite skipped: {exc}",
                warnings=[str(exc)],
            )
        )
        global_warnings.append(f"LLM rewrite error: {exc}")

    # ── H6b. LLM Review UI render (M22) ──────────────────────────────
    if workflow_input.write_llm_review_ui and llm_rewrite_result_path:
        try:
            from resume_pdf_agent.llm_review_ui import render_llm_review_ui_from_result_file

            llm_review_path = output_dir / "llm_review.html"
            review_result = render_llm_review_ui_from_result_file(
                llm_rewrite_result_path, llm_review_path
            )
            if review_result.output_path:
                llm_review_ui_path = str(review_result.output_path)
                all_artifacts.append(
                    WorkflowArtifact(
                        artifact_type="llm_review_ui",
                        path=str(review_result.output_path),
                        description="Browser LLM rewrite review page (static HTML)",
                    )
                )
        except Exception as exc:
            global_warnings.append(f"LLM review UI render failed: {exc}")
    elif workflow_input.write_llm_review_ui and not llm_rewrite_result_path:
        global_warnings.append(
            "write_llm_review_ui is true but no LLM rewrite result was generated. "
            "Enable --enable-llm-rewriting to generate candidates first."
        )

    # ── I. PDF generation ──────────────────────────────────────────────────
    # M23 advisory LLM review decision summary. This never mutates resume content.
    if workflow_input.write_llm_review_decision_summary:
        if not workflow_input.llm_review_decisions_path:
            global_warnings.append(
                "write_llm_review_decision_summary is true but no LLM review decisions path was provided."
            )
        else:
            try:
                from resume_pdf_agent.llm_review_decisions import (
                    summarize_llm_review_decisions_to_files,
                )

                summary_json_path = Path(
                    workflow_input.llm_review_decision_summary_json_path
                    or (output_dir / "llm_rewrite_review_decision_summary.json")
                )
                summary_md_path = Path(
                    workflow_input.llm_review_decision_summary_md_path
                    or (output_dir / "llm_rewrite_review_decision_summary.md")
                )
                result_path_for_summary = (
                    llm_rewrite_result_path
                    if llm_rewrite_result_path and Path(llm_rewrite_result_path).is_file()
                    else None
                )
                summary_result = summarize_llm_review_decisions_to_files(
                    decisions_path=workflow_input.llm_review_decisions_path,
                    result_path=result_path_for_summary,
                    output_json_path=summary_json_path,
                    output_md_path=summary_md_path,
                )
                llm_review_decision_summary_json_path = str(summary_json_path)
                llm_review_decision_summary_md_path = str(summary_md_path)
                all_artifacts.extend(
                    [
                        WorkflowArtifact(
                            artifact_type="llm_review_decision_summary_json",
                            path=str(summary_json_path),
                            description="Advisory LLM review decision summary JSON",
                        ),
                        WorkflowArtifact(
                            artifact_type="llm_review_decision_summary_markdown",
                            path=str(summary_md_path),
                            description="Advisory LLM review decision summary Markdown",
                        ),
                    ]
                )
                stage_status = WorkflowStageStatus.COMPLETED
                if summary_result.warnings:
                    stage_status = WorkflowStageStatus.COMPLETED_WITH_WARNINGS
                    global_warnings.extend(summary_result.warnings)
                stages.append(
                    _stage_result(
                        WorkflowStageName.LLM_REVIEW_DECISION_SUMMARY,
                        stage_status,
                        (
                            "LLM review decisions summarized; "
                            f"decisions: {summary_result.total_decisions}; "
                            f"approved: {summary_result.approved_count}; "
                            f"ignored: {summary_result.ignored_count}"
                        ),
                        warnings=list(summary_result.warnings),
                    )
                )
            except Exception as exc:
                global_warnings.append(f"LLM review decision summary failed: {exc}")
                stages.append(
                    _stage_result(
                        WorkflowStageName.LLM_REVIEW_DECISION_SUMMARY,
                        WorkflowStageStatus.COMPLETED_WITH_WARNINGS,
                        f"LLM review decision summary skipped: {exc}",
                        warnings=[str(exc)],
                    )
                )

    # M24 plan-only LLM candidate application artifact. This never mutates resume content.
    if workflow_input.write_llm_application_plan:
        if not llm_rewrite_result_path:
            global_warnings.append(
                "write_llm_application_plan is true but no LLM rewrite result was generated."
            )
        elif not workflow_input.llm_review_decisions_path:
            global_warnings.append(
                "write_llm_application_plan is true but no LLM review decisions path was provided."
            )
        else:
            try:
                from resume_pdf_agent.llm_application_plan import (
                    plan_llm_candidate_application_to_files,
                )

                plan_json_path = Path(
                    workflow_input.llm_application_plan_json_path
                    or (output_dir / "llm_rewrite_application_plan.json")
                )
                plan_md_path = Path(
                    workflow_input.llm_application_plan_md_path
                    or (output_dir / "llm_rewrite_application_plan.md")
                )
                summary_path_for_plan = (
                    workflow_input.llm_review_decision_summary_json_path
                    or llm_review_decision_summary_json_path
                )
                if not summary_path_for_plan or not Path(summary_path_for_plan).is_file():
                    summary_path_for_plan = None

                plan_result = plan_llm_candidate_application_to_files(
                    result_path=llm_rewrite_result_path,
                    decisions_path=workflow_input.llm_review_decisions_path,
                    summary_path=summary_path_for_plan,
                    output_json_path=plan_json_path,
                    output_md_path=plan_md_path,
                )
                llm_application_plan_json_path = str(plan_json_path)
                llm_application_plan_md_path = str(plan_md_path)
                all_artifacts.extend(
                    [
                        WorkflowArtifact(
                            artifact_type="llm_application_plan_json",
                            path=str(plan_json_path),
                            description="Plan-only LLM candidate application JSON",
                        ),
                        WorkflowArtifact(
                            artifact_type="llm_application_plan_markdown",
                            path=str(plan_md_path),
                            description="Plan-only LLM candidate application Markdown",
                        ),
                    ]
                )
                stage_status = WorkflowStageStatus.COMPLETED
                if plan_result.warnings:
                    stage_status = WorkflowStageStatus.COMPLETED_WITH_WARNINGS
                    global_warnings.extend(plan_result.warnings)
                stages.append(
                    _stage_result(
                        WorkflowStageName.LLM_APPLICATION_PLAN,
                        stage_status,
                        (
                            "LLM candidate application plan generated; "
                            f"planned: {plan_result.planned_count}; "
                            f"blocked: {plan_result.blocked_count}; "
                            f"needs edit: {plan_result.needs_manual_edit_count}; "
                            f"excluded: {plan_result.excluded_count}; "
                            f"unmapped: {plan_result.unmapped_count}"
                        ),
                        warnings=list(plan_result.warnings),
                    )
                )
            except Exception as exc:
                global_warnings.append(f"LLM application plan failed: {exc}")
                stages.append(
                    _stage_result(
                        WorkflowStageName.LLM_APPLICATION_PLAN,
                        WorkflowStageStatus.COMPLETED_WITH_WARNINGS,
                        f"LLM application plan skipped: {exc}",
                        warnings=[str(exc)],
                    )
                )

    # M25 local static manual preview UI. This never mutates resume content.
    if workflow_input.write_llm_application_preview_ui:
        plan_path_for_preview = (
            llm_application_plan_json_path
            or workflow_input.llm_application_plan_json_path
        )
        if not plan_path_for_preview or not Path(plan_path_for_preview).is_file():
            global_warnings.append(
                "write_llm_application_preview_ui is true but no LLM application plan JSON was available."
            )
            stages.append(
                _stage_result(
                    WorkflowStageName.LLM_APPLICATION_PREVIEW_UI,
                    WorkflowStageStatus.COMPLETED_WITH_WARNINGS,
                    "LLM application preview UI skipped: missing application plan JSON.",
                    warnings=[
                        "No LLM application plan JSON was available for preview rendering."
                    ],
                )
            )
        else:
            try:
                from resume_pdf_agent.llm_application_preview_ui import (
                    render_llm_application_preview_ui_from_plan_file,
                )

                preview_path = Path(
                    workflow_input.llm_application_preview_ui_path
                    or (output_dir / "llm_rewrite_application_preview.html")
                )
                preview_result = render_llm_application_preview_ui_from_plan_file(
                    plan_path_for_preview,
                    preview_path,
                )
                if preview_result.output_path:
                    llm_application_preview_ui_path = str(preview_result.output_path)
                    all_artifacts.append(
                        WorkflowArtifact(
                            artifact_type="llm_application_preview_ui",
                            path=str(preview_result.output_path),
                            description="Manual plan-only LLM candidate application preview UI",
                        )
                    )
                    stage_status = WorkflowStageStatus.COMPLETED
                    if preview_result.warnings:
                        stage_status = WorkflowStageStatus.COMPLETED_WITH_WARNINGS
                        global_warnings.extend(preview_result.warnings)
                    stages.append(
                        _stage_result(
                            WorkflowStageName.LLM_APPLICATION_PREVIEW_UI,
                            stage_status,
                            (
                                "LLM application preview UI rendered; "
                                f"planned: {preview_result.planned_count}; "
                                f"blocked: {preview_result.blocked_count}; "
                                f"needs edit: {preview_result.needs_manual_edit_count}; "
                                f"excluded: {preview_result.excluded_count}; "
                                f"unmapped: {preview_result.unmapped_count}"
                            ),
                            warnings=list(preview_result.warnings),
                        )
                    )
                else:
                    global_warnings.extend(preview_result.errors)
                    stages.append(
                        _stage_result(
                            WorkflowStageName.LLM_APPLICATION_PREVIEW_UI,
                            WorkflowStageStatus.COMPLETED_WITH_WARNINGS,
                            f"LLM application preview UI skipped: {preview_result.summary}",
                            warnings=list(preview_result.errors),
                        )
                    )
            except Exception as exc:
                global_warnings.append(f"LLM application preview UI failed: {exc}")
                stages.append(
                    _stage_result(
                        WorkflowStageName.LLM_APPLICATION_PREVIEW_UI,
                        WorkflowStageStatus.COMPLETED_WITH_WARNINGS,
                        f"LLM application preview UI skipped: {exc}",
                        warnings=[str(exc)],
                    )
                )

    # ── M26. Pre-application validation ──────────────────────────────
    _m26_plan_for_validation = (
        workflow_input.llm_application_plan_json_path
        or (str(output_dir / "llm_rewrite_application_plan.json"))
    )

    if workflow_input.write_llm_pre_application_validation and Path(_m26_plan_for_validation).is_file():
        try:
            from resume_pdf_agent.llm_pre_application_validation import (
                write_pre_application_validation_to_files,
            )

            val_json_path = Path(
                workflow_input.llm_pre_application_validation_json_path
                or (output_dir / "llm_rewrite_pre_application_validation.json")
            )
            val_md_path = Path(
                workflow_input.llm_pre_application_validation_md_path
                or (output_dir / "llm_rewrite_pre_application_validation.md")
            )

            val_report = write_pre_application_validation_to_files(
                plan_path=_m26_plan_for_validation,
                output_json_path=val_json_path,
                output_md_path=val_md_path,
                result_path=llm_rewrite_result_path,
                decisions_path=workflow_input.llm_review_decisions_path,
                summary_path=workflow_input.llm_review_decision_summary_json_path,
                strict=False,
            )

            llm_pre_application_validation_json_path = str(val_json_path)
            llm_pre_application_validation_md_path = str(val_md_path)

            all_artifacts.append(
                WorkflowArtifact(
                    artifact_type="llm_pre_application_validation",
                    path=str(val_json_path),
                    description="Strict pre-application validation report (JSON)",
                )
            )
            all_artifacts.append(
                WorkflowArtifact(
                    artifact_type="llm_pre_application_validation",
                    path=str(val_md_path),
                    description="Strict pre-application validation report (Markdown)",
                )
            )

            stages.append(
                _stage_result(
                    WorkflowStageName.LLM_PRE_APPLICATION_VALIDATION,
                    WorkflowStageStatus.COMPLETED_WITH_WARNINGS if val_report.global_warnings else WorkflowStageStatus.COMPLETED,
                    (
                        f"Pre-application validation: {val_report.passed_count} passed, "
                        f"{val_report.blocked_count} blocked, "
                        f"{val_report.needs_manual_edit_count} needs edit, "
                        f"{val_report.excluded_count} excluded, "
                        f"{val_report.unmapped_count} unmapped; "
                        f"can proceed: {'Yes' if val_report.can_proceed_to_patch_preview else 'No'}"
                    ),
                    warnings=list(val_report.global_warnings),
                )
            )
            if val_report.global_warnings:
                global_warnings.extend(val_report.global_warnings)
        except Exception as exc:
            global_warnings.append(f"Pre-application validation failed: {exc}")
            stages.append(
                _stage_result(
                    WorkflowStageName.LLM_PRE_APPLICATION_VALIDATION,
                    WorkflowStageStatus.COMPLETED_WITH_WARNINGS,
                    f"Pre-application validation skipped: {exc}",
                    warnings=[str(exc)],
                )
            )
    elif workflow_input.write_llm_pre_application_validation:
        global_warnings.append(
            "write_llm_pre_application_validation is true but no application plan was found. "
            "Generate an application plan first via --write-llm-application-plan."
        )
        stages.append(
            _stage_result(
                WorkflowStageName.LLM_PRE_APPLICATION_VALIDATION,
                WorkflowStageStatus.COMPLETED_WITH_WARNINGS,
                "Pre-application validation skipped: missing application plan JSON.",
                warnings=[
                    "No LLM application plan JSON was available for pre-application validation."
                ],
            )
        )

    # ── M27. Manual patch preview ───────────────────────────────────
    _m27_plan_for_preview = (
        workflow_input.llm_application_plan_json_path
        or str(output_dir / "llm_rewrite_application_plan.json")
    )
    _m27_val_for_preview = (
        workflow_input.llm_pre_application_validation_json_path
        or str(output_dir / "llm_rewrite_pre_application_validation.json")
    )

    if (
        workflow_input.write_llm_manual_patch_preview
        and Path(_m27_plan_for_preview).is_file()
        and Path(_m27_val_for_preview).is_file()
    ):
        try:
            from resume_pdf_agent.llm_manual_patch_preview import (
                write_manual_patch_preview_to_files,
            )

            pv_json_path = Path(
                workflow_input.llm_manual_patch_preview_json_path
                or (output_dir / "llm_rewrite_manual_patch_preview.json")
            )
            pv_md_path = Path(
                workflow_input.llm_manual_patch_preview_md_path
                or (output_dir / "llm_rewrite_manual_patch_preview.md")
            )
            pv_html_path = Path(
                workflow_input.llm_manual_patch_preview_html_path
                or (output_dir / "llm_rewrite_manual_patch_preview.html")
            )

            pv_report = write_manual_patch_preview_to_files(
                plan_path=_m27_plan_for_preview,
                validation_path=_m27_val_for_preview,
                output_json_path=pv_json_path,
                output_md_path=pv_md_path,
                output_html_path=pv_html_path,
            )

            llm_manual_patch_preview_json_path = str(pv_json_path)
            llm_manual_patch_preview_md_path = str(pv_md_path)
            llm_manual_patch_preview_html_path = str(pv_html_path)

            all_artifacts.append(WorkflowArtifact(
                artifact_type="llm_manual_patch_preview",
                path=str(pv_json_path),
                description="Manual patch preview (JSON) — preview only",
            ))
            all_artifacts.append(WorkflowArtifact(
                artifact_type="llm_manual_patch_preview",
                path=str(pv_md_path),
                description="Manual patch preview (Markdown) — preview only",
            ))
            all_artifacts.append(WorkflowArtifact(
                artifact_type="llm_manual_patch_preview",
                path=str(pv_html_path),
                description="Manual patch preview (HTML) — preview only",
            ))

            stages.append(_stage_result(
                WorkflowStageName.LLM_MANUAL_PATCH_PREVIEW,
                WorkflowStageStatus.COMPLETED_WITH_WARNINGS if pv_report.global_warnings else WorkflowStageStatus.COMPLETED,
                (
                    f"Manual patch preview: {pv_report.preview_ready_count} ready, "
                    f"{pv_report.blocked_count} blocked, "
                    f"{pv_report.needs_manual_edit_count} needs edit, "
                    f"{pv_report.excluded_count} excluded, "
                    f"{pv_report.unmapped_count} unmapped"
                ),
                warnings=list(pv_report.global_warnings),
            ))
            if pv_report.global_warnings:
                global_warnings.extend(pv_report.global_warnings)
        except Exception as exc:
            global_warnings.append(f"Manual patch preview failed: {exc}")
    elif workflow_input.write_llm_manual_patch_preview:
        global_warnings.append(
            "write_llm_manual_patch_preview is true but plan or validation is missing."
        )

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
        parsed_jd_path=parsed_jd_path,
        jd_criteria_profile_path=jd_criteria_profile_path,
        jd_compliance_status=jd_compliance_status,
        used_user_provided_jd=used_user_provided_jd,
        llm_rewrite_result_path=llm_rewrite_result_path,
        llm_rewriting_used=llm_rewriting_used,
        confirmation_ui_path=confirmation_ui_path,
        llm_review_ui_path=llm_review_ui_path,
        llm_review_decision_summary_json_path=llm_review_decision_summary_json_path,
        llm_review_decision_summary_md_path=llm_review_decision_summary_md_path,
        llm_application_plan_json_path=llm_application_plan_json_path,
        llm_application_plan_md_path=llm_application_plan_md_path,
        llm_application_preview_ui_path=llm_application_preview_ui_path,
        llm_pre_application_validation_json_path=llm_pre_application_validation_json_path,
        llm_pre_application_validation_md_path=llm_pre_application_validation_md_path,
        llm_manual_patch_preview_json_path=llm_manual_patch_preview_json_path,
        llm_manual_patch_preview_md_path=llm_manual_patch_preview_md_path,
        llm_manual_patch_preview_html_path=llm_manual_patch_preview_html_path,
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
    parsed_jd_path: str | None = None,
    jd_criteria_profile_path: str | None = None,
    jd_compliance_status: str | None = None,
    used_user_provided_jd: bool = False,
    llm_rewrite_result_path: str | None = None,
    llm_rewriting_used: bool = False,
    confirmation_ui_path: str | None = None,
    llm_review_ui_path: str | None = None,
    llm_review_decision_summary_json_path: str | None = None,
    llm_review_decision_summary_md_path: str | None = None,
    llm_application_plan_json_path: str | None = None,
    llm_application_plan_md_path: str | None = None,
    llm_application_preview_ui_path: str | None = None,
    llm_pre_application_validation_json_path: str | None = None,
    llm_pre_application_validation_md_path: str | None = None,
    llm_manual_patch_preview_json_path: str | None = None,
    llm_manual_patch_preview_md_path: str | None = None,
    llm_manual_patch_preview_html_path: str | None = None,
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
        parsed_jd_path=parsed_jd_path,
        jd_criteria_profile_path=jd_criteria_profile_path,
        jd_compliance_status=jd_compliance_status,
        used_user_provided_jd=used_user_provided_jd,
        llm_rewrite_result_path=llm_rewrite_result_path,
        llm_rewriting_used=llm_rewriting_used,
        confirmation_ui_path=confirmation_ui_path,
        llm_review_ui_path=llm_review_ui_path,
        llm_review_decision_summary_json_path=llm_review_decision_summary_json_path,
        llm_review_decision_summary_md_path=llm_review_decision_summary_md_path,
        llm_application_plan_json_path=llm_application_plan_json_path,
        llm_application_plan_md_path=llm_application_plan_md_path,
        llm_application_preview_ui_path=llm_application_preview_ui_path,
        llm_pre_application_validation_json_path=None,
        llm_pre_application_validation_md_path=None,
        llm_manual_patch_preview_json_path=None,
        llm_manual_patch_preview_md_path=None,
        llm_manual_patch_preview_html_path=None,
    )
