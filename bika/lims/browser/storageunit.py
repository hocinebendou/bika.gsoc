from bika.sanbi.controlpanel.bika_storageinventories import StorageInventoriesView


class StorageUnitInventoryView(StorageInventoriesView):
    def __init__(self, context, request):
        super(StorageUnitInventoryView, self).__init__(context, request)