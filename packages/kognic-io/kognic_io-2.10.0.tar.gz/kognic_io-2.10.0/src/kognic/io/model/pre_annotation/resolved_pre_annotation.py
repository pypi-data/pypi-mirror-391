from datetime import datetime

from kognic.openlabel.models.models import OpenLabelAnnotation

from kognic.io.model.base_serializer import BaseSerializer


class ResolvedPreAnnotation(BaseSerializer):
    uuid: str
    scene_uuid: str
    external_id: str
    created: datetime
    content: OpenLabelAnnotation
