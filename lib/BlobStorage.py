import os
import glob
import json
import time


class BlobStorage:
    ROBOT_LIBRARY_SCOPE = 'SUITE'

    def wait_for_blob_file(self, blob_root, device_id, operation_hours, timeout=60):
        """
        Polls blob_root/{device_id}/{operation_hours}/ for any .json file.
        Returns the parsed content as a dict and deletes the file.
        Raises TimeoutError if no file appears within timeout seconds.
        """
        directory = os.path.join(str(blob_root), str(device_id), str(operation_hours))
        end_time = time.time() + float(timeout)
        while time.time() < end_time:
            files = glob.glob(os.path.join(directory, "*.json"))
            if files:
                file_path = files[0]
                with open(file_path, "r") as f:
                    data = json.load(f)
                os.remove(file_path)
                return data
            time.sleep(5.0)
        raise TimeoutError(
            f"No blob file appeared in '{directory}' within {timeout}s"
        )

    def get_nested_value(self, data, field_path):
        """
        Extract a value from a nested dict using a dot-separated path.
        e.g. "RefeerOperatingMode.AutomaticColdTreatmentMode" →
             data["RefeerOperatingMode"]["AutomaticColdTreatmentMode"]
        """
        value = data
        for key in str(field_path).split("."):
            value = value[key]
        return value
