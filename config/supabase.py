"""
Supabase client configuration and utility functions
"""
from supabase import create_client, Client
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def get_supabase_client() -> Client:
    """
    Create and return a Supabase client instance
    """
    try:
        supabase: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
        return supabase
    except Exception as e:
        logger.error(f"Error creating Supabase client: {e}")
        return None


def get_supabase_admin_client() -> Client:
    """
    Create and return a Supabase client instance with service role key (admin)
    """
    try:
        supabase: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_KEY
        )
        return supabase
    except Exception as e:
        logger.error(f"Error creating Supabase admin client: {e}")
        return None


class SupabaseStorage:
    """
    Utility class for Supabase Storage operations
    """

    def __init__(self, bucket_name='oral-cancer-images'):
        # Use admin client (service role) for storage operations
        self.client = get_supabase_admin_client()
        self.bucket_name = bucket_name

    def upload_file(self, file_path: str, file_data: bytes, content_type: str = 'image/jpeg'):
        """
        Upload a file to Supabase Storage

        Args:
            file_path: Path in the bucket where file will be stored
            file_data: Binary file data
            content_type: MIME type of the file

        Returns:
            dict: Upload response or None if failed
        """
        try:
            response = self.client.storage.from_(self.bucket_name).upload(
                file_path,
                file_data,
                file_options={"content-type": content_type, "upsert": "true"}
            )
            return response
        except Exception as e:
            logger.error(f"Error uploading file to Supabase: {e}")
            return None

    def get_public_url(self, file_path: str) -> str:
        """
        Get public URL for a file in Supabase Storage

        Args:
            file_path: Path of the file in the bucket

        Returns:
            str: Public URL of the file
        """
        try:
            response = self.client.storage.from_(self.bucket_name).get_public_url(file_path)
            return response
        except Exception as e:
            logger.error(f"Error getting public URL: {e}")
            return None

    def download_file(self, file_path: str):
        """
        Download a file from Supabase Storage

        Args:
            file_path: Path of the file in the bucket

        Returns:
            bytes: File data or None if failed
        """
        try:
            response = self.client.storage.from_(self.bucket_name).download(file_path)
            return response
        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            return None

    def delete_file(self, file_path: str):
        """
        Delete a file from Supabase Storage

        Args:
            file_path: Path of the file in the bucket

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            response = self.client.storage.from_(self.bucket_name).remove([file_path])
            return True
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return False

    def list_files(self, folder_path: str = ''):
        """
        List files in a folder in Supabase Storage

        Args:
            folder_path: Path of the folder in the bucket

        Returns:
            list: List of files or None if failed
        """
        try:
            response = self.client.storage.from_(self.bucket_name).list(folder_path)
            return response
        except Exception as e:
            logger.error(f"Error listing files: {e}")
            return None
