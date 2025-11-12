import os
import shutil
from base64 import b64encode
from datetime import datetime
import logging
import requests
import subprocess
from dotenv import load_dotenv
from huggingface_hub import snapshot_download

load_dotenv()

from .CephS3Manager import CephS3Manager

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ProjectsAPI manages ClearML project operations
class ProjectsAPI:
    def __init__(self, post, verbose):
        self.verbose = verbose
        if self.verbose:
            print("Initializing ProjectsAPI...")
        self._post = post
        print("[OK] ProjectsAPI initialized successfully")

    def create(self, name, description=""):
        if self.verbose:
            print(f"Preparing to create project: name={name}, description={description}")
        print(f"Starting to create project: name={name}, description={description}")
        response = self._post("/projects.create", {"name": name, "description": description})
        if not response or "id" not in response:
            error_msg = "Failed to create project in ClearML"
            print(f"[FAIL] {error_msg}")
            raise ValueError(error_msg)
        if self.verbose:
            print(f"Project creation completed: id={response['id']}")
        print(f"[OK] Project created successfully: id={response['id']}")
        return response

    def get_all(self):
        if self.verbose:
            print("Preparing to retrieve all projects...")
        print("Starting to get all projects...")
        response = self._post("/projects.get_all")
        if not response or "projects" not in response:
            error_msg = "Failed to retrieve projects from ClearML"
            print(f"[FAIL] {error_msg}")
            raise ValueError(error_msg)
        if self.verbose:
            print(f"Projects retrieval completed: found {len(response['projects'])} projects")
        print(f"[OK] Retrieved {len(response['projects'])} projects successfully")
        return response["projects"]

# ModelsAPI manages ClearML model operations
class ModelsAPI:
    def __init__(self, post, verbose):
        self.verbose = verbose
        if self.verbose:
            print("Initializing ModelsAPI...")
        self._post = post
        print("[OK] ModelsAPI initialized successfully")

    def get_all(self, project_id=None):
        if self.verbose:
            print(f"Preparing to retrieve models for project_id={project_id}")
        print(f"Starting to get all models for project_id={project_id}")
        payload = {"project": project_id} if project_id else {}
        response = self._post("/models.get_all", payload)

        # Check expected key in proper format
        if isinstance(response, dict):
            if "models" in response and isinstance(response["models"], list):
                if self.verbose:
                    print(f"Models retrieval completed: found {len(response['models'])} models")
                print(f"[OK] Retrieved {len(response['models'])} models successfully")
                return response["models"]
            if "data" in response and isinstance(response["data"], dict) and "models" in response["data"]:
                if self.verbose:
                    print(f"Models retrieval completed: found {len(response['data']['models'])} models")
                print(f"[OK] Retrieved {len(response['data']['models'])} models successfully")
                return response["data"]["models"]

        error_msg = f"'models' not found in response: {response}"
        print(f"[ERROR] {error_msg}")
        raise ValueError("Failed to retrieve models from ClearML")
        return []

    def create(self, name, project_id, metadata=None, uri=""):
        if self.verbose:
            print(f"Preparing to create model: name={name}, project_id={project_id}, uri={uri}")
        print(f"Starting to create model: name={name}, project_id={project_id}, uri={uri}")
        payload = {
            "name": name,
            "project": project_id,
            "uri": uri
        }

        if isinstance(metadata, dict):
            payload["metadata"] = metadata

        response = self._post("/models.create", payload)
        if not response or "id" not in response:
            error_msg = "Failed to create model in ClearML"
            print(f"[FAIL] {error_msg}")
            raise ValueError(error_msg)
        if self.verbose:
            print(f"Model creation completed: id={response['id']}")
        print(f"[OK] Model created successfully: id={response['id']}")
        return response

    def update(self, model_id, uri=None, metadata=None):
        if self.verbose:
            print(f"Preparing to update model: model_id={model_id}, uri={uri}")
        print(f"Starting to update model: model_id={model_id}, uri={uri}")
        payload = {"model": model_id}
        if uri:
            payload["uri"] = uri
        if isinstance(metadata, dict) or isinstance(metadata, list):
            payload["metadata"] = metadata

        response = self._post("/models.add_or_update_metadata", payload)
        if not response:
            error_msg = "Failed to update model metadata in ClearML"
            print(f"[FAIL] {error_msg}")
            raise ValueError(error_msg)
        if self.verbose:
            print(f"Model metadata update completed for id={model_id}")
        print(f"[OK] Model metadata updated successfully for id={model_id}")
        return response

    def edit_uri(self, model_id, uri):
        if self.verbose:
            print(f"Preparing to edit URI for model_id={model_id}, uri={uri}")
        print(f"Starting to edit URI for model_id={model_id}, uri={uri}")
        payload = {"model": model_id, "uri": uri}
        response = self._post("/models.edit", payload)
        if not response:
            error_msg = "Failed to edit model URI in ClearML"
            print(f"[FAIL] {error_msg}")
            raise ValueError(error_msg)
        if self.verbose:
            print(f"Model URI edit completed for id={model_id}")
        print(f"[OK] Model URI edited successfully for id={model_id}")
        return response

    def get_by_id(self, model_id):
        if self.verbose:
            print(f"Preparing to retrieve model by id: {model_id}")
        print(f"Starting to get model by id: {model_id}")
        response = self._post("/models.get_by_id", {"model": model_id})
        if not response:
            error_msg = f"Failed to retrieve model with ID {model_id} from ClearML"
            print(f"[FAIL] {error_msg}")
            raise ValueError(error_msg)
        if self.verbose:
            print(f"Model retrieval completed: id={model_id}")
        print(f"[OK] Model retrieved successfully: id={model_id}")
        return response

    def delete(self, model_id):
        if self.verbose:
            print(f"Preparing to delete model: id={model_id}")
        print(f"Starting to delete model: id={model_id}")
        response = self._post("/models.delete", {"model": model_id})
        if not response:
            error_msg = f"Failed to delete model with ID {model_id} from ClearML"
            print(f"[FAIL] {error_msg}")
            raise ValueError(error_msg)
        if self.verbose:
            print(f"Model deletion completed: id={model_id}")
        print(f"[OK] Model deleted successfully: id={model_id}")
        return response

# MLOpsManager integrates ClearML and Ceph S3 operations
class MLOpsManager:
    def get_user_info(self):
        return requests.get(
            os.path.join(self.USER_MANAGEMENT_API, f"user/{self.CLEARML_USERNAME}/metadata?token={self.USER_TOKEN}"),
            timeout=10
        ).json()

    def __init__(
        self,
        user_name,
        user_token,
        CLEARML_API_SERVER_URL=None,
        CEPH_ENDPOINT_URL=None,
        USER_MANAGEMENT_API=None,
        verbose=False
    ):
        self.verbose = verbose
        if self.verbose:
            print("Initializing MLOpsManager...")
        print("Starting MLOpsManager initialization...")
        # Load defaults from environment
        self.CLEARML_USERNAME = user_name
        self.USER_TOKEN = user_token
        self.CLEARML_API_SERVER_URL = CLEARML_API_SERVER_URL or os.environ.get("CLEARML_API_HOST")
        self.USER_MANAGEMENT_API = USER_MANAGEMENT_API or os.environ.get("USER_MANAGEMENT_API")
        self.CEPH_ENDPOINT_URL = CEPH_ENDPOINT_URL or os.environ.get("CEPH_ENDPOINT_URL")

        # Validate required ClearML credentials
        if self.verbose:
            print("Validating ClearML credentials...")
        if not all([self.CLEARML_API_SERVER_URL, self.CLEARML_USERNAME, self.USER_MANAGEMENT_API, self.CEPH_ENDPOINT_URL]):
            error_msg = "Missing required ClearML configuration parameters"
            print(f"[FAIL] {error_msg}")
            raise ValueError(error_msg)
        if self.verbose:
            print("ClearML credentials validated successfully")
        user_info = self.get_user_info()
        # Ceph configuration from environment
        self.CEPH_ADMIN_ACCESS_KEY = user_info["s3_access_key"]
        self.CEPH_ADMIN_SECRET_KEY = user_info["s3_secret_key"]
        self.CEPH_USER_BUCKET = user_info["s3_bucket"]
        self.CLEARML_ACCESS_KEY = user_info["clearml_access_key"]
        self.CLEARML_SECRET_KEY = user_info["clearml_secret_key"]
        
        # Health checks for ClearML services
        if self.verbose:
            print("Performing ClearML service health checks...")
        if not self.check_clearml_service():
            error_msg = "ClearML Server down."
            print(f"[FAIL] {error_msg}")
            raise ValueError(error_msg)
        if not self.check_clearml_auth():
            error_msg = "ClearML Authentication not correct."
            print(f"[FAIL] {error_msg}")
            raise ValueError(error_msg)
        if self.verbose:
            print("ClearML service health checks completed")

        # Initialize CephS3Manager with user-specific bucket
        if self.verbose:
            print("Initializing CephS3Manager...")
        self.ceph = CephS3Manager(
            self.CEPH_ENDPOINT_URL,
            self.CEPH_ADMIN_ACCESS_KEY,
            self.CEPH_ADMIN_SECRET_KEY,
            self.CEPH_USER_BUCKET,
            verbose=self.verbose
        )
        if self.verbose:
            print("CephS3Manager initialized successfully")

        # Login to ClearML and extract token
        if self.verbose:
            print("Preparing to login to ClearML...")
        print("Logging in to ClearML...")
        creds = f"{self.CLEARML_ACCESS_KEY}:{self.CLEARML_SECRET_KEY}"
        auth_header = b64encode(creds.encode("utf-8")).decode("utf-8")
        res = requests.post(
            f"{self.CLEARML_API_SERVER_URL}/auth.login",
            headers={"Authorization": f"Basic {auth_header}"}
        )
        if res.status_code != 200:
            error_msg = "Failed to authenticate with ClearML"
            print(f"[FAIL] {error_msg}")
            raise ValueError(error_msg)
        self.token = res.json()["data"]["token"]
        if self.verbose:
            print("ClearML login completed successfully")
        print("[OK] Logged in to ClearML successfully")

        self.projects = ProjectsAPI(self._post, verbose=self.verbose)
        self.models = ModelsAPI(self._post, verbose=self.verbose)

        # Get or create user-specific project
        if self.verbose:
            print("Checking for user-specific project...")
        print("Getting or creating user-specific project...")
        projects = self.projects.get_all()
        self.project_name = f"project_{self.CLEARML_USERNAME}"
        exists = [p for p in projects if p["name"] == self.project_name]
        self.project_id = exists[0]["id"] if exists else self.projects.create(self.project_name)["id"]
        if self.verbose:
            print(f"User-specific project processing completed: project_id={self.project_id}")
        print(f"[OK] Project ID: {self.project_id}")
        print("[OK] MLOpsManager initialized successfully")

    def _post(self, path, params=None):
        if self.verbose:
            print(f"Preparing POST request to {path}...")
        print(f"Starting POST request to {path}...")
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            res = requests.post(f"{self.CLEARML_API_SERVER_URL}{path}", headers=headers, json=params)
            res.raise_for_status()

            data = res.json()
            if "data" not in data:
                error_msg = f"No 'data' key in response: {data}"
                print(f"[ERROR] {error_msg}")
                raise ValueError(f"Request to {path} failed: No data in response")
            if self.verbose:
                print(f"POST request to {path} completed successfully")
            print(f"[OK] POST request to {path} successful")
            return data["data"]

        except requests.exceptions.RequestException as e:
            error_msg = f"Request to {path} failed: {e}"
            print(f"[ERROR] {error_msg}")
            print(f"[ERROR] Status Code: {res.status_code}, Response: {res.text}")
            raise ValueError(f"Request to {path} failed: {str(e)}")

        except ValueError as e:
            error_msg = f"Failed to parse JSON from {path}: {e}"
            print(f"[ERROR] {error_msg}")
            print(f"[ERROR] Raw response: {res.text}")
            raise ValueError(f"Failed to parse JSON from {path}: {str(e)}")

    def check_clearml_service(self):
        """
        Check if ClearML service is reachable and responding.
        """
        if self.verbose:
            print("Preparing to check ClearML service...")
        print("Checking ClearML service...")
        try:
            r = requests.get(self.CLEARML_API_SERVER_URL + "/auth.login", timeout=5)
            if r.status_code in [200, 401]:
                if self.verbose:
                    print("ClearML service check completed")
                print("[OK] ClearML Service")
                return True
            error_msg = f"ClearML Service {r.status_code}"
            print(f"[FAIL] {error_msg}")
            raise ValueError("ClearML Service is not reachable")
        except Exception as e:
            error_msg = f"ClearML Service: {str(e)}"
            print(f"[FAIL] {error_msg}")
            raise ValueError("ClearML Service is not reachable")

    def check_clearml_auth(self):
        """
        Check if ClearML credentials are valid by attempting login.
        """
        if self.verbose:
            print("Preparing to check ClearML authentication...")
        print("Checking ClearML authentication...")
        try:
            creds = f"{self.CLEARML_ACCESS_KEY}:{self.CLEARML_SECRET_KEY}"
            auth_header = b64encode(creds.encode("utf-8")).decode("utf-8")
            r = requests.post(
                self.CLEARML_API_SERVER_URL + "/auth.login",
                headers={"Authorization": f"Basic {auth_header}"},
                timeout=5
            )
            if r.status_code == 200:
                if self.verbose:
                    print("ClearML authentication check completed")
                print("[OK] ClearML Auth")
                return True
            error_msg = f"ClearML Auth {r.status_code}"
            print(f"[FAIL] {error_msg}")
            raise ValueError("ClearML Authentication failed")
        except Exception as e:
            error_msg = f"ClearML Auth: {str(e)}"
            print(f"[FAIL] {error_msg}")
            raise ValueError("ClearML Authentication failed")

    def get_model_id_by_name(self, name):
        if self.verbose:
            print(f"Preparing to get model ID for name: {name}")
        print(f"Starting to get model ID by name: {name}")
        models = self.models.get_all(self.project_id)
        if self.verbose:
            print(f"Retrieved {len(models)} models for ID lookup")
        for m in models:
            if m["name"] == name:
                if self.verbose:
                    print(f"Model ID lookup completed: id={m['id']}")
                print(f"[OK] Model ID found: {m['id']}")
                return m["id"]
        if self.verbose:
            print("Model ID lookup completed: no model found")
        print("[OK] No model found with given name")
        return None

    def get_model_name_by_id(self, model_id):
        if self.verbose:
            print(f"Preparing to get model name for ID: {model_id}")
        print(f"Starting to get model name by ID: {model_id}")
        model = self.models.get_by_id(model_id)
        result = model.get("name") if model else None
        if result:
            if self.verbose:
                print(f"Model name lookup completed: name={result}")
            print(f"[OK] Model name found: {result}")
        else:
            if self.verbose:
                print("Model name lookup completed: no model found")
            print("[OK] No model found with given ID")
        return result

    def generate_random_string(self):
        if self.verbose:
            print("Preparing to generate random string...")
        print("Generating random string...")
        import random
        import string
        result = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        if self.verbose:
            print(f"Random string generation completed: {result}")
        print(f"[OK] Random string generated: {result}")
        return result

    def transfer_from_s3(self, source_endpoint_url, source_access_key, source_secret_key, source_bucket, source_path, dest_prefix, exclude=[".git", ".DS_Store"], overwrite=True):
        """
        Transfer a model from another S3 bucket to the initialized bucket.
        """
        if self.verbose:
            print(f"Preparing transfer from S3: source_path={source_path}, dest_prefix={dest_prefix}")
        print(f"Starting transfer from S3: source_path={source_path}, dest_prefix={dest_prefix}")
        tmp_dir = None
        try:
            tmp_dir = f"./tmp_{self.generate_random_string()}"
            if self.verbose:
                print(f"Creating temporary directory: {tmp_dir}")
            print(f"Creating temporary directory: {tmp_dir}")
            os.makedirs(tmp_dir, exist_ok=True)

            if self.verbose:
                print("Initializing source CephS3Manager...")
            print("Initializing source CephS3Manager...")
            src_ceph = CephS3Manager(source_endpoint_url, source_access_key, source_secret_key, source_bucket)
            if self.verbose:
                print("Source CephS3Manager initialized")
            print("Downloading from source...")
            src_ceph.download(source_path, tmp_dir, keep_folder=True, exclude=exclude, overwrite=overwrite)

            if self.verbose:
                print("Preparing to delete destination folder if exists...")
            print("Deleting destination folder if exists...")
            self.ceph.delete_folder(dest_prefix)  # Ensure clean state
            if self.verbose:
                print("Destination folder deletion completed")
            print("Uploading to destination...")
            self.ceph.upload(tmp_dir, dest_prefix)

            if self.verbose:
                print("S3 transfer completed successfully")
            print("[OK] Transfer from S3 successful")
            return True
        except Exception as e:
            error_msg = f"Failed to transfer model from S3: {e}"
            print(f"[FAIL] {error_msg}")
            try:
                self.ceph.delete_folder(dest_prefix)
            except Exception as cleanup_error:
                print(f"[ERROR] Failed to clean up destination folder {dest_prefix}: {cleanup_error}")
            raise ValueError(f"Failed to transfer model from S3: {str(e)}")
        finally:
            if tmp_dir and os.path.exists(tmp_dir):
                try:
                    shutil.rmtree(tmp_dir)
                    if self.verbose:
                        print(f"Temporary directory cleanup completed: {tmp_dir}")
                    print(f"[OK] Cleaned up temporary directory {tmp_dir}")
                except Exception as cleanup_error:
                    print(f"[ERROR] Failed to clean up temporary directory {tmp_dir}: {cleanup_error}")

    def add_model(self, source_type, model_name=None, source_path=None, code_path=None,
                  external_ceph_endpoint_url=None, external_ceph_bucket_name=None, external_ceph_access_key=None, external_ceph_secret_key=None):
        """
        Add a model from various sources (local, Hugging Face, or S3) and register it in ClearML.
        """
        if self.verbose:
            print(f"Preparing to add model: source_type={source_type}, model_name={model_name}")
        print(f"Starting to add model: source_type={source_type}, model_name={model_name}")
        # Input validation
        if not model_name or not isinstance(model_name, str):
            error_msg = "Model name is required"
            logger.error(error_msg)
            print(f"[ERROR] model_name must be a non-empty string")
            return None
        if source_type not in ["local", "hf", "s3"]:
            error_msg = f"Unknown source_type: {source_type}"
            logger.error(error_msg)
            print(f"[ERROR] {error_msg}")
            return None
        if source_type == "local":
            if not source_path or not os.path.exists(source_path):
                error_msg = f"Local path {source_path} does not exist"
                logger.error(error_msg)
                print(f"[FAIL] {error_msg}")
                return None
            if not os.access(source_path, os.R_OK):
                error_msg = f"Cannot read source_path: {source_path}"
                logger.error(error_msg)
                print(f"[FAIL] {error_msg}")
                return None
        if source_type == "hf" and (not source_path or not isinstance(source_path, str)):
            error_msg = f"Invalid or missing source_path for Hugging Face: {source_path}"
            logger.error(error_msg)
            print(f"[FAIL] {error_msg}")
            return None
        if source_type == "s3" and (
            not all([source_path, external_ceph_access_key, external_ceph_secret_key, external_ceph_endpoint_url, external_ceph_bucket_name])
            or not all(isinstance(x, str) for x in [source_path, external_ceph_access_key, external_ceph_secret_key, external_ceph_endpoint_url, external_ceph_bucket_name])
        ):
            error_msg = "Missing required S3 parameters"
            logger.error(error_msg)
            print(f"[FAIL] {error_msg}")
            return None
        if code_path and (not os.path.isfile(code_path) or not code_path.endswith(".py")):
            error_msg = f"Invalid code_path: {code_path}. Must be a valid .py file"
            logger.error(error_msg)
            print(f"[FAIL] {error_msg}")
            return None

        if self.verbose:
            print("Checking for existing model...")
        print("Checking if model already exists...")
        if self.get_model_id_by_name(model_name):
            warning_msg = f"Model with name '{model_name}' already exists."
            logger.warning(warning_msg)
            print(f"[WARN] {warning_msg}")
            print("[INFO] Listing existing models:")
            self.list_models(verbose=True)
            return None

        # Determine model_folder_name according to source_type
        if source_type == "hf":
            model_folder_name = f"hf_{model_name}"
        elif source_type == "local":
            model_folder_name = os.path.basename(source_path)
        elif source_type == "s3":
            model_folder_name = os.path.basename(source_path)
        else:
            model_folder_name = ""

        if self.verbose:
            print(f"Model folder name set: {model_folder_name}")
        print(f"Model folder name determined: {model_folder_name}")
        have_model_py = False
        temp_model_id = self.generate_random_string()
        dest_prefix = f"models/{temp_model_id}/"
        local_path = None
        temp_local_path = None

        try:
            if source_type == "local":
                # Create a temporary copy to protect source_path
                temp_local_path = f"./tmp_{self.generate_random_string()}"
                if self.verbose:
                    print(f"Preparing to copy local source to temporary path: {temp_local_path}")
                print(f"Copying local source to temporary path: {temp_local_path}")
                shutil.copytree(source_path, temp_local_path, dirs_exist_ok=True)
                if self.verbose:
                    print("Local source copy completed")
                print("Deleting destination prefix if exists...")
                self.ceph.delete_folder(dest_prefix)  # Ensure clean state
                if self.verbose:
                    print("Destination prefix deletion completed")
                print("Uploading temporary path...")
                size_mb = self.ceph.upload(temp_local_path, dest_prefix)
            elif source_type == "hf":
                if self.verbose:
                    print("Preparing to download from Hugging Face...")
                print("Downloading from Hugging Face...")
                local_path = snapshot_download(repo_id=source_path)
                if self.verbose:
                    print("Hugging Face download completed")
                print("Deleting destination prefix if exists...")
                self.ceph.delete_folder(dest_prefix)  # Ensure clean state
                if self.verbose:
                    print("Destination prefix deletion completed")
                print("Uploading HF model...")
                size_mb = self.ceph.upload(local_path, os.path.join(dest_prefix, model_folder_name))
            elif source_type == "s3":
                if self.verbose:
                    print("Preparing to transfer from S3...")
                print("Transferring from S3...")
                success = self.transfer_from_s3(
                    source_endpoint_url=external_ceph_endpoint_url,
                    source_access_key=external_ceph_access_key,
                    source_secret_key=external_ceph_secret_key,
                    source_bucket=external_ceph_bucket_name,
                    source_path=source_path,
                    dest_prefix=dest_prefix,
                    exclude=[".git", ".DS_Store"],
                    overwrite=True
                )
                if not success:
                    error_msg = "Failed to transfer model from S3"
                    print(f"[FAIL] {error_msg}")
                    raise ValueError(error_msg)
                uri = f"s3://{self.ceph.bucket_name}/{dest_prefix}"
                if self.verbose:
                    print("Calculating size of transferred model...")
                print("Getting size of transferred model...")
                size_mb = self.ceph.get_uri_size(uri)
            else:
                error_msg = f"Unknown source_type: {source_type}"
                print(f"[FAIL] {error_msg}")
                raise ValueError(error_msg)

            if code_path and os.path.isfile(code_path):
                if self.verbose:
                    print("Preparing to upload model.py code...")
                print("Uploading model.py code...")
                self.ceph.upload(code_path, dest_prefix + "model.py")
                have_model_py = True
                if self.verbose:
                    print("model.py upload completed")

            # Create model in ClearML after successful upload
            if self.verbose:
                print("Preparing to create model in ClearML...")
            print("Creating model in ClearML...")
            model = self.models.create(
                name=model_name,
                project_id=self.project_id,
                uri="s3://dummy/uri"
            )

            model_id = model["id"]
            if model_id != temp_model_id:
                new_dest_prefix = f"models/{model_id}/"
                if self.verbose:
                    print(f"Preparing to move folder to new prefix: {new_dest_prefix}")
                print(f"Moving folder to new prefix: {new_dest_prefix}")
                if self.ceph.check_if_exists(new_dest_prefix):
                    self.ceph.delete_folder(new_dest_prefix)
                self.ceph.move_folder(dest_prefix, new_dest_prefix)
                self.ceph.delete_folder(dest_prefix)
                dest_prefix = new_dest_prefix
                if self.verbose:
                    print("Folder move completed")

            if self.verbose:
                print("Preparing model metadata...")
            print("Preparing metadata...")
            metadata_list = [
                {"key": "modelFolderName", "type": "str", "value": model_folder_name},
                {"key": "haveModelPy", "type": "str", "value": str(have_model_py).lower()},
                {"key": "modelSize", "type": "float", "value": str(size_mb) if size_mb is not None else "0.0"}
            ]

            uri = f"s3://{self.ceph.bucket_name}/{dest_prefix}"
            if self.verbose:
                print("Preparing to edit model URI...")
            print("Editing model URI...")
            self.models.edit_uri(model_id, uri=uri)
            if self.verbose:
                print("Model URI edit completed")
            print("Updating model metadata...")
            self.models.update(model_id, metadata=metadata_list)
            if self.verbose:
                print("Model metadata update completed")

            logger.info(f"Model '{model_name}' (ID: {model_id}) added successfully")
            print(f"[SUCCESS] Model '{model_name}' (ID: {model_id}) added successfully")
            return model_id

        except (Exception, KeyboardInterrupt) as e:
            error_msg = f"Upload or registration failed: {e}"
            logger.error(error_msg)
            print(f"[ERROR] {error_msg}")
            print("[INFO] Cleaning up partially uploaded model...")
            if 'model_id' in locals():
                try:
                    self.models.delete(model_id)
                    if self.verbose:
                        print("ClearML model cleanup completed")
                    print("[OK] Cleaned up ClearML model")
                except Exception as cleanup_error:
                    error_cleanup = f"Failed to clean up ClearML model {model_id}: {cleanup_error}"
                    logger.error(error_cleanup)
                    print(f"[ERROR] {error_cleanup}")
            if dest_prefix:
                try:
                    self.ceph.delete_folder(dest_prefix)
                    if self.verbose:
                        print("Ceph folder cleanup completed")
                    print("[OK] Cleaned up Ceph folder")
                except Exception as cleanup_error:
                    error_cleanup = f"Failed to clean up Ceph folder {dest_prefix}: {cleanup_error}"
                    logger.error(error_cleanup)
                    print(f"[ERROR] {error_cleanup}")
            return None
        finally:
            # Clean up temporary local paths
            for path in [local_path, temp_local_path]:
                if path and os.path.exists(path):
                    try:
                        shutil.rmtree(path)
                        if self.verbose:
                            print(f"Local directory cleanup completed: {path}")
                        print(f"[OK] Cleaned up local directory {path}")
                    except Exception as cleanup_error:
                        error_cleanup = f"Failed to clean up local directory {path}: {cleanup_error}"
                        logger.error(error_cleanup)
                        print(f"[ERROR] {error_cleanup}")

    def get_model(self, model_name, local_dest):
        """
        Download a model by name and return its metadata.
        """
        logger.info("Starting get_model for name=%r, dest=%r", model_name, local_dest)
        if self.verbose:
            print(f"Preparing to get model: model_name={model_name}, local_dest={local_dest}")
        print(f"Starting get_model: model_name={model_name}, local_dest={local_dest}")

        # Resolve model ID
        try:
            if self.verbose:
                print("Preparing to resolve model ID...")
            print("Resolving model ID...")
            model_id = self.get_model_id_by_name(model_name)
            logger.debug("Resolved model_id=%r for name=%r", model_id, model_name)
            if self.verbose:
                print(f"Model ID resolution completed: id={model_id}")
            print(f"[OK] Resolved model_id={model_id}")
        except Exception as exc:
            error_msg = f"Failed to resolve model ID for name: {model_name}"
            logger.exception(error_msg)
            print(f"[FAIL] {error_msg}")
            raise ValueError(error_msg) from exc

        if not model_id:
            warning_msg = f"Model not found: {model_name}"
            logger.warning(warning_msg)
            print(f"[WARN] {warning_msg}")
            raise ValueError(warning_msg)

        # Fetch model metadata
        try:
            if self.verbose:
                print("Preparing to fetch model metadata...")
            print("Fetching model metadata...")
            model_data = self.models.get_by_id(model_id)
            logger.debug("Fetched model_data keys=%s", list(model_data.keys()))
            if self.verbose:
                print("Model metadata fetch completed")
            print("[OK] Model metadata fetched")
        except Exception as exc:
            error_msg = f"Failed to fetch model data for id: {model_id}"
            logger.exception(error_msg)
            print(f"[FAIL] {error_msg}")
            raise ValueError(error_msg) from exc

        # Preserve original extraction logic
        model = model_data.get("model") or model_data
        logger.debug("Normalized model payload type=%s keys=%s", type(model).__name__, list(model.keys()))
        if self.verbose:
            print("Normalizing model payload...")
        print("Model payload normalized")

        # Extract URI
        try:
            uri = model["uri"]
            logger.debug("Model URI: %r", uri)
            if self.verbose:
                print(f"URI extraction completed: {uri}")
            print(f"[OK] Extracted URI: {uri}")
        except Exception as exc:
            error_msg = f"Model metadata missing 'uri' field for id: {model_id}"
            logger.exception(error_msg)
            print(f"[FAIL] {error_msg}")
            raise ValueError(error_msg) from exc

        # Derive remote path
        try:
            _, remote_path = uri.replace("s3://", "").split("/", 1)
            logger.debug("Derived remote_path=%r from uri=%r", remote_path, uri)
            if self.verbose:
                print(f"Remote path derivation completed: {remote_path}")
            print(f"[OK] Derived remote_path: {remote_path}")
        except Exception as exc:
            error_msg = f"Invalid model URI format: {uri!r}"
            logger.exception(error_msg)
            print(f"[FAIL] {error_msg}")
            raise ValueError(error_msg) from exc

        # Download via ceph client
        try:
            logger.info("Downloading from remote_path=%r to local_dest=%r", remote_path, local_dest)
            if self.verbose:
                print(f"Preparing to download model from {remote_path} to {local_dest}...")
            print(f"Downloading model from {remote_path} to {local_dest}...")
            self.ceph.download(
                remote_path,
                local_dest,
                keep_folder=True,
                exclude=[".git", ".DS_Store"],
                overwrite=False,
            )
            logger.info("Download complete for model id=%r, name=%r", model_id, model_name)
            if self.verbose:
                print("Model download completed")
            print(f"[OK] Download complete for model: {model_name}")
        except Exception as exc:
            error_msg = f"Failed to download model from {remote_path!r} to {local_dest!r}"
            logger.exception(error_msg)
            print(f"[FAIL] {error_msg}")
            raise ValueError(error_msg) from exc

        logger.info("Returning model metadata for name=%r", model_name)
        if self.verbose:
            print("Preparing to return model metadata...")
        print("[OK] Returning model metadata")
        return model

    def get_model_info(self, identifier):
        if self.verbose:
            print(f"Preparing to get model info for identifier: {identifier}")
        print(f"Starting to get model info for identifier: {identifier}")
        all_models = self.models.get_all(self.project_id)
        if self.verbose:
            print(f"Retrieved {len(all_models)} models for info lookup")

        def extract_model_info(model):
            print("=" * 40)
            print(f"ID: {model.get('id')}")
            print(f"Name: {model.get('name')}")
            print(f"Created: {model.get('created')}")
            print(f"Framework: {model.get('framework')}")
            print(f"URI: {model.get('uri')}")

            # Extract and show metadata (including modelSize)
            metadata = model.get("metadata", {})
            print("Metadata:")
            for key, value in metadata.items():
                print(f"  - {key}: {value}")

            # Highlight modelSize if available
            model_size = metadata.get("modelSize", {}).get("value")
            if model_size is not None:
                try:
                    print(f"\n[Model Size] {float(model_size):.2f} MB")
                except (ValueError, TypeError):
                    print(f"\n[Model Size] Invalid value: {model_size}")

            print(f"Labels: {model.get('labels')}")
            print("=" * 40)

        # Try match by ID
        if self.verbose:
            print("Attempting to match model by ID...")
        print("Trying to match by ID...")
        matched_by_id = [m for m in all_models if m.get("id") == identifier]
        if matched_by_id:
            extract_model_info(matched_by_id[0])
            if self.verbose:
                print("Model info retrieval by ID completed")
            print("[OK] Model info retrieved by ID")
            return matched_by_id[0]

        # Try match by name
        if self.verbose:
            print("Attempting to match model by name...")
        print("Trying to match by name...")
        matched_by_name = [m for m in all_models if m.get("name") == identifier]
        if matched_by_name:
            for model in matched_by_name:
                extract_model_info(model)
            if self.verbose:
                print("Model info retrieval by name completed")
            print("[OK] Model info retrieved by name")
            return matched_by_name

        info_msg = f"No model found with identifier: '{identifier}'"
        print(f"[INFO] {info_msg}")
        raise ValueError(f"No model found with identifier: '{identifier}'")

    def list_models(self, verbose=True):
        if self.verbose:
            print("Preparing to list models...")
        print("Starting to list models...")
        try:
            models = self.models.get_all(self.project_id)
            if verbose:
                grouped = {}
                for m in models:
                    grouped.setdefault(m["name"], []).append(m["id"])
                for name, ids in grouped.items():
                    print(f"[Model] Name: {name}, Count: {len(ids)}")
            else:
                for m in models:
                    print(f"[Model] {m['name']} (ID: {m['id']})")
            if self.verbose:
                print(f"Model listing completed: found {len(models)} models")
            print(f"[OK] Listed {len(models)} models successfully")
            return [(m["name"], m["id"]) for m in models]
        except Exception as e:
            error_msg = f"Failed to list models: {e}"
            print(f"[FAIL] {error_msg}")
            raise ValueError(f"Failed to list models: {str(e)}")

    def delete_model(self, model_id=None, model_name=None):
        if self.verbose:
            print(f"Preparing to delete model: model_id={model_id}, model_name={model_name}")
        print(f"Starting to delete model: model_id={model_id}, model_name={model_name}")
        if model_name and not model_id:
            if self.verbose:
                print("Resolving model ID from name...")
            model_id = self.get_model_id_by_name(model_name)
            if not model_id:
                warning_msg = f"No model found with name '{model_name}'"
                print(f"[WARN] {warning_msg}")
                raise ValueError(f"No model found with name '{model_name}'")

        if self.verbose:
            print(f"Retrieving model data for id: {model_id}")
        model_data = self.models.get_by_id(model_id)
        if not model_data:
            warning_msg = f"Model with ID '{model_id}' not found."
            print(f"[WARN] {warning_msg}")
            raise ValueError(f"Model with ID '{model_id}' not found")

        model = model_data.get("model") or model_data
        uri = model.get("uri")
        if not uri:
            warning_msg = f"Model '{model_id}' has no 'uri'."
            print(f"[WARN] {warning_msg}")
            raise ValueError(f"Model '{model_id}' has no URI")

        try:
            _, remote_path = uri.replace("s3://", "").split("/", 1)
            if self.verbose:
                print(f"Preparing to delete Ceph folder: {remote_path}")
            print(f"Deleting Ceph folder: {remote_path}")
            self.ceph.delete_folder(remote_path)
            if self.verbose:
                print("Ceph folder deletion completed")
            print("Deleting model from ClearML...")
            self.models.delete(model_id)
            if self.verbose:
                print("ClearML model deletion completed")
            print(f"[SUCCESS] Model '{model_id}' deleted successfully from ClearML and Ceph")
        except Exception as e:
            error_msg = f"Failed to delete model '{model_id}': {e}"
            print(f"[FAIL] {error_msg}")
            raise ValueError(f"Failed to delete model '{model_id}': {str(e)}")
