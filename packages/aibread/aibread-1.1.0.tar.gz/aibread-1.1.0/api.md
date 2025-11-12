# Repo

Types:

```python
from aibread.types import RepoResponse, RepoListResponse
```

Methods:

- <code title="get /v1/repo">client.repo.<a href="./src/aibread/resources/repo.py">list</a>() -> <a href="./src/aibread/types/repo_list_response.py">RepoListResponse</a></code>
- <code title="get /v1/repo/{repo_name}">client.repo.<a href="./src/aibread/resources/repo.py">get</a>(repo_name) -> <a href="./src/aibread/types/repo_response.py">RepoResponse</a></code>
- <code title="put /v1/repo">client.repo.<a href="./src/aibread/resources/repo.py">set</a>(\*\*<a href="src/aibread/types/repo_set_params.py">params</a>) -> <a href="./src/aibread/types/repo_response.py">RepoResponse</a></code>

# Prompts

Types:

```python
from aibread.types import Message, PromptResponse
```

# Targets

Types:

```python
from aibread.types import TargetConfigBase, TargetResponse
```

# Bakes

Types:

```python
from aibread.types import (
    BakeResponse,
    CheckpointConfig,
    DataConfig,
    DatasetItem,
    DeepspeedConfig,
    ModelConfig,
    OptimizerConfig,
    SchedulerConfig,
    WandbConfig,
)
```

# Health

Types:

```python
from aibread.types import HealthCheckResponse
```

Methods:

- <code title="get /v1/health">client.health.<a href="./src/aibread/resources/health.py">check</a>() -> <a href="./src/aibread/types/health_check_response.py">HealthCheckResponse</a></code>
