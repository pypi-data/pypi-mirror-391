"""
Compute Cluster Registry

Manages external compute cluster configurations for DVT.
Clusters are stored in compute.yml in the project root.
"""

import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from dbt.clients.yaml_helper import load_yaml_text
from dbt_common.clients.system import load_file_contents, write_file
from dbt_common.exceptions import DbtRuntimeError


@dataclass
class ComputeCluster:
    """Configuration for an external compute cluster."""

    name: str  # Cluster identifier
    type: str  # 'spark' (currently only Spark supported for external)
    config: Dict[str, Any] = field(default_factory=dict)  # Cluster-specific config
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        result = {
            "name": self.name,
            "type": self.type,
            "config": self.config,
        }
        if self.description:
            result["description"] = self.description
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ComputeCluster":
        """Deserialize from dictionary."""
        return cls(
            name=data["name"],
            type=data["type"],
            config=data.get("config", {}),
            description=data.get("description")
        )


class ComputeRegistry:
    """
    Registry for managing external compute clusters.

    Clusters are stored in compute.yml in the project root directory.
    """

    def __init__(self, project_dir: str):
        """
        Initialize compute registry.

        :param project_dir: Path to project root directory
        """
        self.project_dir = project_dir
        self.compute_file = os.path.join(project_dir, "compute.yml")
        self._clusters: Dict[str, ComputeCluster] = {}
        self._load()

    def _load(self) -> None:
        """Load clusters from compute.yml."""
        if not os.path.exists(self.compute_file):
            # No compute.yml - that's OK, it's optional
            return

        try:
            contents = load_file_contents(self.compute_file, strip=False)
            yaml_content = load_yaml_text(contents)

            if not yaml_content:
                return

            # Parse clusters
            clusters_data = yaml_content.get("clusters", [])
            for cluster_data in clusters_data:
                cluster = ComputeCluster.from_dict(cluster_data)
                self._clusters[cluster.name] = cluster

        except Exception as e:
            raise DbtRuntimeError(
                f"Failed to load compute.yml: {str(e)}"
            ) from e

    def _save(self) -> None:
        """Save clusters to compute.yml."""
        clusters_list = [
            cluster.to_dict()
            for cluster in self._clusters.values()
        ]

        yaml_content = {
            "version": "1.0",
            "clusters": clusters_list
        }

        # Convert to YAML string
        import yaml
        yaml_str = yaml.dump(yaml_content, default_flow_style=False, sort_keys=False)

        # Write to file
        write_file(self.compute_file, yaml_str)

    def register(
        self,
        name: str,
        cluster_type: str,
        config: Dict[str, Any],
        description: Optional[str] = None,
        replace: bool = False
    ) -> None:
        """
        Register a new compute cluster.

        :param name: Cluster name (must be unique)
        :param cluster_type: Type of cluster ('spark')
        :param config: Cluster configuration dict
        :param description: Optional cluster description
        :param replace: If True, replace existing cluster with same name
        :raises DbtRuntimeError: If cluster exists and replace=False
        """
        if name in self._clusters and not replace:
            raise DbtRuntimeError(
                f"Compute cluster '{name}' already exists. Use replace=True to overwrite."
            )

        if cluster_type not in ("spark",):
            raise DbtRuntimeError(
                f"Unsupported cluster type '{cluster_type}'. Supported types: spark"
            )

        cluster = ComputeCluster(
            name=name,
            type=cluster_type,
            config=config,
            description=description
        )

        self._clusters[name] = cluster
        self._save()

    def remove(self, name: str) -> None:
        """
        Remove a compute cluster.

        :param name: Cluster name
        :raises DbtRuntimeError: If cluster not found
        """
        if name not in self._clusters:
            raise DbtRuntimeError(f"Compute cluster '{name}' not found")

        del self._clusters[name]
        self._save()

    def get(self, name: str) -> Optional[ComputeCluster]:
        """
        Get a compute cluster by name.

        :param name: Cluster name
        :returns: ComputeCluster or None if not found
        """
        return self._clusters.get(name)

    def list(self) -> List[ComputeCluster]:
        """
        List all registered clusters.

        :returns: List of ComputeCluster objects
        """
        return list(self._clusters.values())

    def exists(self, name: str) -> bool:
        """
        Check if a cluster exists.

        :param name: Cluster name
        :returns: True if cluster exists
        """
        return name in self._clusters
