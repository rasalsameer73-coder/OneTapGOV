from uuid import UUID
import asyncio
from typing import List

from sqlalchemy import select

from app.core.database import AsyncSessionFactory
from app.models.identity import User
from app.workers.celery_app import celery
from app.services.recommendations import RecommendationService
from app.core.logging import logger


async def _gather_user_ids(batch_size: int = 500) -> List[UUID]:
    async with AsyncSessionFactory() as session:
        result = await session.scalars(select(User.id).where(User.is_active == True))
        return list(result)


from uuid import UUID
import asyncio
from typing import List, Optional
import json

from sqlalchemy import select

from app.core.database import AsyncSessionFactory
from app.models.identity import User
from app.workers.celery_app import celery
from app.services.recommendations import RecommendationService
from app.core.logging import logger


async def _fetch_active_user_ids() -> List[UUID]:
    async with AsyncSessionFactory() as session:
        result = await session.scalars(select(User.id).where(User.is_active == True))
        return list(result)


async def _generate_for_user_async(user_id: UUID) -> dict:
    async with AsyncSessionFactory() as session:
        svc = RecommendationService(session)
        return await svc.generate(user_id)


def _uuid_int(u: UUID) -> int:
    return u.int


def _maybe_import_prometheus():
    try:
        from prometheus_client import CollectorRegistry, Counter, push_to_gateway, Histogram

        return CollectorRegistry, Counter, push_to_gateway, Histogram
    except Exception:
        return None, None, None, None


def _maybe_init_sentry():
    try:
        import sentry_sdk

        return sentry_sdk
    except Exception:
        return None


def _run_sharded_recompute(shard_index: int = 0, shard_count: int = 1, concurrency: int = 10) -> dict:
    """Run recompute in parallel for users belonging to the given shard.

    Args:
        shard_index: zero-based shard id
        shard_count: number of shards (>=1)
        concurrency: number of concurrent user tasks
    Returns:
        dict summary
    """
    registry_cls, Counter, push_to_gateway, Histogram = _maybe_import_prometheus()
    sentry = _maybe_init_sentry()

    if sentry:
        # Sentry initialized by environment in production if desired
        try:
            sentry.init()
        except Exception:
            pass

    async def _main():
        user_ids = await _fetch_active_user_ids()
        # filter by shard
        if shard_count <= 1:
            selected = user_ids
        else:
            selected = [u for u in user_ids if (_uuid_int(u) % shard_count) == shard_index]

        total = len(selected)
        processed = 0
        failures = 0

        sem = asyncio.Semaphore(concurrency)

        async def _worker(u: UUID):
            nonlocal processed, failures
            async with sem:
                try:
                    await _generate_for_user_async(u)
                except Exception as e:
                    failures += 1
                    logger.error("recompute.user_failed", user_id=str(u), error=str(e))
                    if sentry:
                        sentry.capture_exception(e)
                finally:
                    processed += 1

        # schedule tasks in parallel
        tasks = [asyncio.create_task(_worker(u)) for u in selected]
        # progress-aware gather
        if tasks:
            await asyncio.gather(*tasks)

        return {"status": "ok", "total": total, "processed": processed, "failures": failures}

    try:
        result = asyncio.run(_main())
        # push metrics if pushgateway configured
        try:
            if push_to_gateway is not None:
                import os

                pgw = os.environ.get("PUSHGATEWAY_URL")
                if pgw:
                    # create simple registry and counters
                    registry = registry_cls()
                    c = Counter("recompute_users_processed_total", "Users processed by recompute", registry=registry)
                    c.inc(result.get("processed", 0))
                    push_to_gateway(pgw, job="recompute_recommendations", registry=registry)
        except Exception as e:
            try:
                asyncio.run(logger.awarning("metrics_push_failed", error=str(e)))
            except Exception:
                pass
        return result
    except Exception as exc:
        if sentry:
            try:
                sentry.capture_exception(exc)
            except Exception:
                pass
        try:
            asyncio.run(logger.error("recompute.failed", error=str(exc)))
        except Exception:
            pass
        return {"status": "error", "error": str(exc)}


def recompute_recommendations_impl(shard_index: int = 0, shard_count: int = 1, concurrency: int = 10) -> dict:
    return _run_sharded_recompute(shard_index=shard_index, shard_count=shard_count, concurrency=concurrency)


recompute_recommendations = celery.task(name="workers.recompute_recommendations")(recompute_recommendations_impl)


if __name__ == "__main__":
    # Allow running from command line: print JSON summary
    import sys
    import json as _json

    shard_index = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    shard_count = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    concurrency = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    out = recompute_recommendations_impl(shard_index=shard_index, shard_count=shard_count, concurrency=concurrency)
    print(_json.dumps(out))
