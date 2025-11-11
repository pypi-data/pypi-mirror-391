from time import sleep
from typing import (
    Any,
)

from django.core.management.base import (
    BaseCommand,
)

from django.core.cache import (
    cache,
)

from edu_rdm_integration.stages.upload_data.operations import (
    UploadData,
)
from edu_rdm_integration.stages.upload_data.queues import (
    RdmDictBasedSubStageAttachmentQueue
)


class Command(BaseCommand):
    """Команда для отправки данных в витрину параллельно-последовательно. В рамках скрипта последовательно,
    параллельно количетвом запусков команды."""

    help = 'Команда для отправки данных в витрину параллельно-последовательно'  # noqa: A003


    def handle(self, *args: tuple[Any], **kwargs: dict[str, Any]) -> None:
        """Обработчик команды."""
        while True:
            self.stdout.write(f'Начало отправки данных в витрину')

            queue = RdmDictBasedSubStageAttachmentQueue()
            upload_data = UploadData(
                data_cache=cache,
                queue=queue,
            )

            upload_result = upload_data.upload_data()

            sleep(40)

            self.stdout.write(f'Общий объем отправленных файлов {upload_result["total_file_size"]}')
            self.stdout.write(f'Сущности, отправленные в витрину {upload_result["uploaded_entities"]}')