# app/dependencies.py
from fastapi import Header, HTTPException, status
from app.config import SECRET_MODIFY_KEY


def verify_modify_key(x_modify_key: str = Header(..., alias="X-Modify-Key")):
    """
    所有修改【原始数据】的接口，都必须带此依赖。
    请求头示例：X-Modify-Key: your-secret
    """
    if x_modify_key != SECRET_MODIFY_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid modify key",
        )
