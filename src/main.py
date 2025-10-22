# src/main.py
import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from src.graph import run_pipeline_for_pairs


def main():
    load_dotenv()

    pairs = os.getenv("PAIRS", "EURUSD,GBPUSD,USDJPY,AUDUSD,AUDCAD,GBPCAD").split(",")
    pairs = [p.strip().upper() for p in pairs]

    # 👇 Control dry-run via .env
    dry_run_flag = os.getenv("EMAIL_DRYRUN", "True").lower() == "true"

    print(f"\n🚀 Starting daily forex strategy run ({datetime.now(timezone.utc).isoformat()})")
    print(f"📊 Pairs: {', '.join(pairs)}")
    print(f"📧 Email mode: {'DRY-RUN (no email sent)' if dry_run_flag else 'LIVE (emails will be sent)'}\n")

    run_pipeline_for_pairs(pairs, dry_run_email=dry_run_flag)


if __name__ == "__main__":
    main()