import asyncio

from sqlalchemy import select

from app.core.database import AsyncSessionLocal

from app.modules.schemes.models import (
    Scheme,
    SchemeVersion,
    EligibilityRule,
    RuleCondition,
)

from app.modules.documents.models import (
    SchemeDocument,
)

from app.seeders.education_data import (
    education_schemes,
)

from app.seeders.women_data import (
    women_schemes,
)

from app.seeders.agriculture_data import (
    agriculture_schemes,
)


async def seed_schemes():

    all_schemes = (
        education_schemes
        + women_schemes
        + agriculture_schemes
    )

    async with AsyncSessionLocal() as db:

        for scheme_data in all_schemes:

            existing_scheme = await db.execute(
                select(Scheme).where(
                    Scheme.scheme_code
                    == scheme_data["scheme_code"]
                )
            )

            existing_scheme = (
                existing_scheme.scalar_one_or_none()
            )

            if existing_scheme:

                print(
                    f"{scheme_data['scheme_name']} already exists"
                )

                continue

            scheme = Scheme(
                scheme_name=scheme_data["scheme_name"],
                scheme_code=scheme_data["scheme_code"],
            )

            db.add(scheme)

            await db.flush()

            version = SchemeVersion(
                scheme_id=scheme.id,
                version_number=1,
                is_current=True,
            )

            db.add(version)

            await db.flush()

            rule = EligibilityRule(
                scheme_version_id=version.id,
                rule_name="Basic Eligibility",
                logical_operator="AND",
            )

            db.add(rule)

            await db.flush()

            for condition_data in scheme_data[
                "conditions"
            ]:

                condition = RuleCondition(
                    eligibility_rule_id=rule.id,

                    field_name=condition_data[
                        "field_name"
                    ],

                    comparison_operator=condition_data[
                        "comparison_operator"
                    ],

                    comparison_value=condition_data[
                        "comparison_value"
                    ],

                    human_readable_condition=condition_data[
                        "human_readable_condition"
                    ],
                )

                db.add(condition)

            for document_name in scheme_data[
                "documents"
            ]:

                document = SchemeDocument(
                    scheme_id=scheme.id,
                    document_name=document_name,
                )

                db.add(document)

            print(
                f"Seeded: {scheme.scheme_name}"
            )

        await db.commit()


if __name__ == "__main__":
    asyncio.run(
        seed_schemes()
    )