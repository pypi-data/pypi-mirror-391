# Chat

Types:

```python
from premai.types import ChatCompletionsResponse
```

Methods:

- <code title="post /api/v1/chat/completions">client.chat.<a href="./src/premai/resources/chat.py">completions</a>(\*\*<a href="src/premai/types/chat_completions_params.py">params</a>) -> <a href="./src/premai/types/chat_completions_response.py">ChatCompletionsResponse</a></code>

# Models

Types:

```python
from premai.types import (
    ModelListResponse,
    ModelCheckStatusResponse,
    ModelLoadResponse,
    ModelUnloadResponse,
)
```

Methods:

- <code title="get /api/v1/models">client.models.<a href="./src/premai/resources/models.py">list</a>() -> <a href="./src/premai/types/model_list_response.py">ModelListResponse</a></code>
- <code title="get /api/v1/models/running">client.models.<a href="./src/premai/resources/models.py">check_status</a>(\*\*<a href="src/premai/types/model_check_status_params.py">params</a>) -> <a href="./src/premai/types/model_check_status_response.py">ModelCheckStatusResponse</a></code>
- <code title="post /api/v1/models/up">client.models.<a href="./src/premai/resources/models.py">load</a>(\*\*<a href="src/premai/types/model_load_params.py">params</a>) -> <a href="./src/premai/types/model_load_response.py">ModelLoadResponse</a></code>
- <code title="post /api/v1/models/down">client.models.<a href="./src/premai/resources/models.py">unload</a>(\*\*<a href="src/premai/types/model_unload_params.py">params</a>) -> <a href="./src/premai/types/model_unload_response.py">ModelUnloadResponse</a></code>

# Projects

Types:

```python
from premai.types import ProjectCreateResponse, ProjectListResponse, ProjectGetTreeResponse
```

Methods:

- <code title="post /api/v1/public/projects/create">client.projects.<a href="./src/premai/resources/projects.py">create</a>(\*\*<a href="src/premai/types/project_create_params.py">params</a>) -> <a href="./src/premai/types/project_create_response.py">ProjectCreateResponse</a></code>
- <code title="get /api/v1/public/projects">client.projects.<a href="./src/premai/resources/projects.py">list</a>() -> <a href="./src/premai/types/project_list_response.py">ProjectListResponse</a></code>
- <code title="get /api/v1/public/projects/{projectId}">client.projects.<a href="./src/premai/resources/projects.py">get_tree</a>(project_id) -> <a href="./src/premai/types/project_get_tree_response.py">ProjectGetTreeResponse</a></code>

# Datasets

Types:

```python
from premai.types import (
    DatasetAddDatapointResponse,
    DatasetCreateFromJSONLResponse,
    DatasetCreateSyntheticResponse,
    DatasetGetResponse,
)
```

Methods:

- <code title="post /api/v1/datasets/{datasetId}/addDatapoint">client.datasets.<a href="./src/premai/resources/datasets.py">add_datapoint</a>(dataset_id, \*\*<a href="src/premai/types/dataset_add_datapoint_params.py">params</a>) -> <a href="./src/premai/types/dataset_add_datapoint_response.py">DatasetAddDatapointResponse</a></code>
- <code title="post /api/v1/public/datasets/create-from-jsonl">client.datasets.<a href="./src/premai/resources/datasets.py">create_from_jsonl</a>(\*\*<a href="src/premai/types/dataset_create_from_jsonl_params.py">params</a>) -> <a href="./src/premai/types/dataset_create_from_jsonl_response.py">DatasetCreateFromJSONLResponse</a></code>
- <code title="post /api/v1/public/datasets/create-synthetic">client.datasets.<a href="./src/premai/resources/datasets.py">create_synthetic</a>(\*\*<a href="src/premai/types/dataset_create_synthetic_params.py">params</a>) -> <a href="./src/premai/types/dataset_create_synthetic_response.py">DatasetCreateSyntheticResponse</a></code>
- <code title="get /api/v1/public/datasets/{datasetId}">client.datasets.<a href="./src/premai/resources/datasets.py">get</a>(dataset_id) -> <a href="./src/premai/types/dataset_get_response.py">DatasetGetResponse</a></code>

# Snapshots

Types:

```python
from premai.types import SnapshotCreateResponse, SnapshotCreateFromFilesResponse
```

Methods:

- <code title="post /api/v1/public/snapshots/create">client.snapshots.<a href="./src/premai/resources/snapshots.py">create</a>(\*\*<a href="src/premai/types/snapshot_create_params.py">params</a>) -> <a href="./src/premai/types/snapshot_create_response.py">SnapshotCreateResponse</a></code>
- <code title="post /api/v1/public/snapshots/create-from-files">client.snapshots.<a href="./src/premai/resources/snapshots.py">create_from_files</a>(\*\*<a href="src/premai/types/snapshot_create_from_files_params.py">params</a>) -> <a href="./src/premai/types/snapshot_create_from_files_response.py">SnapshotCreateFromFilesResponse</a></code>

# Recommendations

Types:

```python
from premai.types import RecommendationGenerateResponse, RecommendationGetResponse
```

Methods:

- <code title="post /api/v1/public/recommendations/generate">client.recommendations.<a href="./src/premai/resources/recommendations.py">generate</a>(\*\*<a href="src/premai/types/recommendation_generate_params.py">params</a>) -> <a href="./src/premai/types/recommendation_generate_response.py">RecommendationGenerateResponse</a></code>
- <code title="get /api/v1/public/recommendations/{snapshotId}">client.recommendations.<a href="./src/premai/resources/recommendations.py">get</a>(snapshot_id) -> <a href="./src/premai/types/recommendation_get_response.py">RecommendationGetResponse</a></code>

# Finetuning

Types:

```python
from premai.types import FinetuningCreateResponse, FinetuningGetResponse
```

Methods:

- <code title="post /api/v1/public/finetuning/create">client.finetuning.<a href="./src/premai/resources/finetuning.py">create</a>(\*\*<a href="src/premai/types/finetuning_create_params.py">params</a>) -> <a href="./src/premai/types/finetuning_create_response.py">FinetuningCreateResponse</a></code>
- <code title="get /api/v1/public/finetuning/{jobId}">client.finetuning.<a href="./src/premai/resources/finetuning.py">get</a>(job_id) -> <a href="./src/premai/types/finetuning_get_response.py">FinetuningGetResponse</a></code>
