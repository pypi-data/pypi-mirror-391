import json
import logging
from pathlib import Path

from pydantic import BaseModel

logger = logging.getLogger(__name__)


VEFAAS_IAM_CRIDENTIAL_PATH = "/var/run/secrets/iam/credential"


class VeIAMCredential(BaseModel):
    access_key_id: str
    secret_access_key: str
    session_token: str


def get_credential_from_vefaas_iam() -> VeIAMCredential:
    """Get credential from VeFaaS IAM file"""
    logger.info(
        f"Get Volcegnine access key or secret key from environment variables failed, try to get from VeFaaS IAM file (path={VEFAAS_IAM_CRIDENTIAL_PATH})."
    )

    path = Path(VEFAAS_IAM_CRIDENTIAL_PATH)

    if not path.exists():
        logger.error(
            f"Get Volcegnine access key or secret key from environment variables failed, and VeFaaS IAM file (path={VEFAAS_IAM_CRIDENTIAL_PATH}) not exists. Please check your configuration."
        )
        raise FileNotFoundError(
            f"Get Volcegnine access key or secret key from environment variables failed, and VeFaaS IAM file (path={VEFAAS_IAM_CRIDENTIAL_PATH}) not exists. Please check your configuration."
        )

    with open(VEFAAS_IAM_CRIDENTIAL_PATH, "r") as f:
        cred_dict = json.load(f)
        access_key = cred_dict["access_key_id"]
        secret_key = cred_dict["secret_access_key"]
        session_token = cred_dict["session_token"]
        return VeIAMCredential(
            access_key_id=access_key,
            secret_access_key=secret_key,
            session_token=session_token,
        )
