from bika.sanbi.controlpanel.bika_storageinventories import StorageInventoriesView
from bika.sanbi.controlpanel.bika_storagemanagements import StorageManagementsView


class StorageUnitInventoryView(StorageInventoriesView):
    def __init__(self, context, request):
        super(StorageUnitInventoryView, self).__init__(context, request)

class StorageUnitManagementView(StorageManagementsView):
    def __init__(self, context, request):
        super(StorageUnitManagementView, self).__init__(context, request)