"""Generic sample user profile for schema validation."""

from resume_pdf_agent.models import (
    AwardEntry,
    ContactInfo,
    EducationEntry,
    LanguageSkill,
    SkillGroup,
    UserProfile,
)

SAMPLE_USER_PROFILE = UserProfile(
    full_name="Alex Chen",
    contact=ContactInfo(
        email="alex.chen@example.com",
        location="Taipei, Taiwan",
        linkedin="https://www.linkedin.com/in/alex-chen-example",
        github="https://github.com/alex-chen-example",
    ),
    education=[
        EducationEntry(
            institution="Example University",
            degree="Bachelor of Science",
            major="Statistics and Computer Science",
            start_date="2022",
            end_date="2026",
            gpa="3.7/4.0",
            core_courses=[
                "Data Structures",
                "Probability",
                "Statistical Modeling",
                "Database Systems",
            ],
            honors=["Dean's List"],
        )
    ],
    target_roles=["Data Science Intern"],
    target_companies=[],
    target_industries=["Technology", "Analytics"],
    skills=[
        SkillGroup(category="Programming", skills=["Python", "SQL", "R"]),
        SkillGroup(category="Data Tools", skills=["pandas", "NumPy", "scikit-learn"]),
        SkillGroup(category="Visualization", skills=["Matplotlib", "Tableau"]),
    ],
    languages=[
        LanguageSkill(language="English", proficiency="Professional working proficiency"),
        LanguageSkill(language="Mandarin", proficiency="Native"),
    ],
    awards=[
        AwardEntry(
            title="University Data Challenge Finalist",
            issuer="Example University Analytics Club",
            date="2025",
            description="Team project selected for final presentation round.",
        )
    ],
    additional_notes=(
        "Sample profile for schema validation only. Details are generic and not "
        "intended to represent a real applicant."
    ),
)
