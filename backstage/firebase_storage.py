import firebase_admin
from firebase_admin import credentials, storage
from elevenlabs import play


class FirebaseStorage:
    _instance = None

    def __new__(cls):

        service_account_path = "utter-firebase-service-account.json"
        storage_bucket = "utter-1234.appspot.com"

        """
        Implements the Singleton pattern. Ensures only one instance of FirebaseStorage is created.
        """
        if cls._instance is None:
            cls._instance = super(FirebaseStorage, cls).__new__(cls)

            if service_account_path is None or storage_bucket is None:
                raise ValueError(
                    "service_account_path and storage_bucket must be provided for the first instantiation."
                )

            # Initialize the Firebase Admin SDK
            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred, {"storageBucket": storage_bucket})
            cls._instance.bucket = storage.bucket()
            print(f"Bucket '{cls._instance.bucket.name}' initialized successfully.")

        return cls._instance

    def upload_blob(self, source_file_name: str, destination_blob_name: str):
        """
        Uploads a file to the Firebase Storage bucket.
        """
        blob = self.bucket.blob(destination_blob_name)
        generation_match_precondition = 0

        blob.upload_from_filename(
            source_file_name, if_generation_match=generation_match_precondition
        )
        print(f"File {source_file_name} uploaded to {destination_blob_name}.")

    def upload_blob_from_memory(self, contents: bytes, destination_blob_name: str):
        """
        Uploads content from memory to the Firebase Storage bucket.
        """
        blob = self.bucket.blob(destination_blob_name)
        blob.upload_from_string(contents)
        print(f"{destination_blob_name} with contents uploaded to {self.bucket.name}.")

    def download_blob(self, source_blob_name: str, destination_file_name: str):
        """
        Downloads a blob from the Firebase Storage bucket to a local file.
        """
        blob = self.bucket.blob(source_blob_name)
        blob.download_to_filename(destination_file_name)
        print(
            f"Downloaded storage object {source_blob_name} from bucket "
            f"{self.bucket.name} to local file {destination_file_name}."
        )

    def download_blob_into_memory(self, blob_name: str) -> bytes:
        """
        Downloads a blob from the Firebase Storage bucket into memory.
        """
        blob = self.bucket.blob(blob_name)
        contents = blob.download_as_bytes()
        print(f"Downloaded storage object {blob_name} from bucket {self.bucket.name}.")
        return contents


if __name__ == "__main__":
    firebase_storage = FirebaseStorage()
    raw = firebase_storage.download_blob_into_memory(
        "audio/se/1_fika_i_stockholm/chapter_1/b1_l1_cNarrator.mp3"
    )
    play(raw)
