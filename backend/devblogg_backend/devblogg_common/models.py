# devblogg_common/models.py
import uuid
from django.db import models

class BaseModel(models.Model):
    """
    Base model cho tất cả các bảng:
    - Sử dụng UUID làm Primary Key (Scalability).
    - Tự động lưu thời gian tạo/sửa.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class SoftDeleteModel(BaseModel):
    """
    Hỗ trợ Soft Delete theo Business Rule 2.D và 3.B
    """
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    

    class Meta:
        abstract = True