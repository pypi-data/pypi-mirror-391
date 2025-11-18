import json
import os
from typing import Any, Dict, Optional, Union

import aiohttp

from ...exceptions import (
    CollectionNotFoundError,
    DownloadFilesError,
    GetTaskError,
    UploadArtifactsError,
    UploadRequestsError,
)
from ...helper.decorators import require_api_key


class DataOperationsMixin:
    """Data generation and processing operations."""
    
    @require_api_key
    async def upload_artifacts(
        self,
        collection: str,
        file_type: str,
        compressed: Optional[bool] = True
    ) -> Dict[str, Any]:
        """
        Retrieve signed url to upload artifact file to a collection.

        Args:
            collection: Name of collection
            file_type: The extension of the file
            compressed: Whether to compress the file using gzip or not (defaults to True)
        
        Returns:
            API response as a dictionary containing the upload URL

        Raises:
            CollectionNotFoundError: If the collection is not found
            UploadArtifactsError: If the API request fails due to unknown reasons
        """
        params = {
            "file_type": file_type,
            "compressed": str(compressed).lower(),
        }

        response, status = await self._client._terrakio_request("GET", f"collections/{collection}/upload", params=params)

        if status != 200:
            if status == 404:
                raise CollectionNotFoundError(f"Collection {collection} not found", status_code=status)
            raise UploadArtifactsError(f"Upload artifacts failed with status {status}", status_code=status)

        return response

    async def _get_upload_url(
        self,
        collection: str
    ) -> Dict[str, Any]:
        """
        Retrieve signed url to upload requests for a collection.

        Args:
            collection: Name of collection
        
        Returns:
            API response as a dictionary containing the upload URL

        Raises:
            CollectionNotFoundError: If the collection is not found
            UploadRequestsError: If the API request fails due to unknown reasons
        """
        response, status = await self._client._terrakio_request("GET", f"collections/{collection}/upload/requests")

        if status != 200:
            if status == 404:
                raise CollectionNotFoundError(f"Collection {collection} not found", status_code=status)
            raise UploadRequestsError(f"Upload requests failed with status {status}", status_code=status)

        return response

    @require_api_key
    async def _upload_file(self, file_path: str, url: str, use_gzip: bool = True):
        """
        Helper method to upload a JSON file to a signed URL.
        
        Args:
            file_path: Path to the JSON file
            url: Signed URL to upload to
            use_gzip: Whether to compress the file with gzip
        """
        try:
            with open(file_path, 'r') as file:
                json_data = json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"JSON file not found: {file_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in file {file_path}: {e}")
        
        return await self._upload_json_data(json_data, url, use_gzip)

    @require_api_key
    async def _upload_json_data(self, json_data, url: str, use_gzip: bool = True):
        """
        Helper method to upload JSON data directly to a signed URL.
        
        Args:
            json_data: JSON data (dict or list) to upload
            url: Signed URL to upload to
            use_gzip: Whether to compress the data with gzip
        """
        if hasattr(json, 'dumps') and 'ignore_nan' in json.dumps.__code__.co_varnames:
            dumps_kwargs = {'ignore_nan': True}
        else:
            dumps_kwargs = {}
        
        if use_gzip:
            import gzip
            body = gzip.compress(json.dumps(json_data, **dumps_kwargs).encode('utf-8'))
            headers = {
                'Content-Type': 'application/json',
                'Content-Encoding': 'gzip'
            }
        else:
            body = json.dumps(json_data, **dumps_kwargs).encode('utf-8')
            headers = {
                'Content-Type': 'application/json'
            }
        
        response = await self._client._regular_request("PUT", url, data=body, headers=headers)
        return response

    @require_api_key
    async def generate_data(
        self,
        collection: str,
        file_path: str,
        output: str,
        skip_existing: Optional[bool] = True,
        force_loc: Optional[bool] = None,
        server: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate data for a collection.

        Args:
            collection: Name of collection
            file_path: Path to the file to upload
            output: Output type (str)
            force_loc: Write data directly to the cloud under this folder
            skip_existing: Skip existing data
            server: Server to use
        
        Returns:
            API response as a dictionary containing task information

        Raises:
            CollectionNotFoundError: If the collection is not found
            GetTaskError: If the API request fails due to unknown reasons
        """
        
        await self.get_collection(collection = collection)

        upload_urls = await self._get_upload_url(
            collection = collection
        )
        
        url = upload_urls['url']

        await self._upload_file(file_path, url)
        
        payload = {"output": output, "skip_existing": skip_existing}
        
        if force_loc is not None:
            payload["force_loc"] = force_loc
        if server is not None:
            payload["server"] = server
        
        response, status = await self._client._terrakio_request("POST", f"collections/{collection}/generate_data", json=payload)

        if status != 200:
            if status == 404:
                raise CollectionNotFoundError(f"Collection {collection} not found", status_code=status)
            raise GetTaskError(f"Generate data failed with status {status}", status_code=status)
        
        return response

    @require_api_key
    async def post_processing(
        self,
        collection: str,
        folder: str,
        consumer: str
    ) -> Dict[str, Any]:
        """
        Run post processing for a collection.

        Args:
            collection: Name of collection
            folder: Folder to store output
            consumer: Path to post processing script

        Returns:
            API response as a dictionary containing task information

        Raises:
            CollectionNotFoundError: If the collection is not found
            GetTaskError: If the API request fails due to unknown reasons
        """

        await self.get_collection(collection = collection)

        with open(consumer, 'rb') as f:
            form = aiohttp.FormData()
            form.add_field('folder', folder)
            form.add_field(
                'consumer',
                f.read(),
                filename='consumer.py',
                content_type='text/x-python'
            )
        
        response, status = await self._client._terrakio_request(
            "POST",
            f"collections/{collection}/post_process",
            data=form
        )
        
        if status != 200:
            if status == 404:
                raise CollectionNotFoundError(f"Collection {collection} not found", status_code=status)
            raise GetTaskError(f"Post processing failed with status {status}", status_code=status)
        
        return response

    @require_api_key
    async def download_files(
        self,
        collection: str,
        file_type: str,
        page: Optional[int] = 0,
        page_size: Optional[int] = 100,
        folder: Optional[str] = None,
        url: Optional[bool] = True
    ) -> Dict[str, Any]:
        """
        Get list of signed urls to download files in collection, or download the files directly.

        Args:
            collection: Name of collection
            file_type: Type of files to download - must be either 'raw' or 'processed'
            page: Page number (optional, defaults to 0)
            page_size: Number of files to return per page (optional, defaults to 100)
            folder: If processed file type, which folder to download files from (optional)
            url: If True, return signed URLs; if False, download files directly (optional, defaults to True)

        Returns:
            API response as a dictionary containing list of download URLs (if url=True),
            or a dictionary with downloaded file information (if url=False)

        Raises:
            CollectionNotFoundError: If the collection is not found
            DownloadFilesError: If the API request fails due to unknown reasons
            ValueError: If file_type is not 'raw' or 'processed'
        """
        if file_type not in ['raw', 'processed']:
            raise ValueError(f"file_type must be either 'raw' or 'processed', got '{file_type}'")
        
        params = {"file_type": file_type}
        
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page_size"] = page_size
        if folder is not None:
            params["folder"] = folder

        response, status = await self._client._terrakio_request("GET", f"collections/{collection}/download", params=params)

        if status != 200:
            if status == 404:
                raise CollectionNotFoundError(f"Collection {collection} not found", status_code=status)
            raise DownloadFilesError(f"Download files failed with status {status}", status_code=status)
        
        if url:
            return response
        
        downloaded_files = []
        files_to_download = response.get('files', []) if isinstance(response, dict) else []
        
        async with aiohttp.ClientSession() as session:
            for file_info in files_to_download:
                try:
                    file_url = file_info.get('url')
                    filename = file_info.get('file', '')
                    group = file_info.get('group', '')
                    
                    if not file_url:
                        downloaded_files.append({
                            'filename': filename,
                            'group': group,
                            'error': 'No URL provided'
                        })
                        continue
                    
                    async with session.get(file_url) as file_response:
                        if file_response.status == 200:
                            content = await file_response.read()
                            
                            output_dir = folder if folder else "downloads"
                            if group:
                                output_dir = os.path.join(output_dir, group)
                            os.makedirs(output_dir, exist_ok=True)
                            filepath = os.path.join(output_dir, filename)
                            
                            with open(filepath, 'wb') as f:
                                f.write(content)
                            
                            downloaded_files.append({
                                'filename': filename,
                                'group': group,
                                'filepath': filepath,
                                'size': len(content)
                            })
                        else:
                            downloaded_files.append({
                                'filename': filename,
                                'group': group,
                                'error': f"Failed to download: HTTP {file_response.status}"
                            })
                except Exception as e:
                    downloaded_files.append({
                        'filename': file_info.get('file', 'unknown'),
                        'group': file_info.get('group', ''),
                        'error': str(e)
                    })
        
        return {
            'collection': collection,
            'downloaded_files': downloaded_files,
            'total': len(downloaded_files)
        }

    @require_api_key
    async def gen_and_process(
        self,
        collection: str,
        requests_file: Union[str, Any],
        output: str,
        folder: str,
        consumer: Union[str, Any],
        extra: Optional[Dict[str, Any]] = None,
        force_loc: Optional[bool] = False,
        skip_existing: Optional[bool] = True,
        server: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate data and run post-processing in a single task.

        Args:
            collection: Name of collection
            requests_file: Path to JSON file or file object containing request configurations
            output: Output type (str)
            folder: Folder to store output
            consumer: Path to post processing script or file object
            extra: Additional configuration parameters (optional)
            force_loc: Write data directly to the cloud under this folder (optional, defaults to False)
            skip_existing: Skip existing data (optional, defaults to True)
            server: Server to use (optional)

        Returns:
            API response as a dictionary containing task information

        Raises:
            CollectionNotFoundError: If the collection is not found
            GetTaskError: If the API request fails due to unknown reasons
        """
        await self.get_collection(collection = collection)

        upload_urls = await self._get_upload_url(collection=collection)
        url = upload_urls['url']
        
        # Handle requests_file - either file path (str) or file object
        if isinstance(requests_file, str):
            await self._upload_file(requests_file, url)
        else:
            # File object - read JSON and upload directly
            json_data = json.load(requests_file)
            await self._upload_json_data(json_data, url)

        # Handle consumer - either file path (str) or file object
        if isinstance(consumer, str):
            with open(consumer, 'rb') as f:
                consumer_content = f.read()
        else:
            # Assume it's a file object
            consumer_content = consumer.read()
        
        form = aiohttp.FormData()
        form.add_field('output', output)
        form.add_field('force_loc', str(force_loc).lower())
        form.add_field('skip_existing', str(skip_existing).lower())
        
        if server is not None:
            form.add_field('server', server)
        
        form.add_field('extra', json.dumps(extra or {}))
        form.add_field('folder', folder)
        form.add_field(
            'consumer',
            consumer_content,
            filename='consumer.py',
            content_type='text/x-python'
        )
        
        response, status = await self._client._terrakio_request(
            "POST",
            f"collections/{collection}/gen_and_process",
            data=form
        )
        
        if status != 200:
            if status == 404:
                raise CollectionNotFoundError(f"Collection {collection} not found", status_code=status)
            raise GetTaskError(f"Gen and process failed with status {status}", status_code=status)

        return response

