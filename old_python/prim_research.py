"""
Prim Research Tools
Provides experimental design, data collection, reproducible research,
publication tools, and collaboration features.
"""

import json
import uuid
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class ExperimentStatus(Enum):
    """Experiment status"""
    PLANNING = "planning"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StudyType(Enum):
    """Study types"""
    OBSERVATIONAL = "observational"
    EXPERIMENTAL = "experimental"
    SIMULATION = "simulation"
    SURVEY = "survey"
    META_ANALYSIS = "meta_analysis"


@dataclass
class Experiment:
    """Research experiment"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    status: ExperimentStatus = ExperimentStatus.PLANNING
    hypotheses: List[str] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    data: Dict[str, Any] = field(default_factory=dict)
    results: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Publication:
    """Research publication"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    authors: List[str] = field(default_factory=list)
    abstract: str = ""
    content: str = ""
    keywords: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    doi: str = ""
    status: str = "draft"
    created_at: datetime = field(default_factory=datetime.now)


class ExperimentalDesign:
    """Experimental design tools"""

    def __init__(self):
        self.designs: Dict[str, Dict[str, Any]] = {}

    def create_factorial_design(self, factors: Dict[str, List[Any]]) -> Dict[str, Any]:
        """Create factorial design"""
        from itertools import product

        # Generate all combinations
        factor_names = list(factors.keys())
        factor_values = list(factors.values())

        treatments = list(product(*factor_values))

        design = {
            "type": "factorial",
            "factors": factors,
            "treatments": [
                {name: value for name, value in zip(factor_names, treatment)}
                for treatment in treatments
            ],
            "num_treatments": len(treatments)
        }

        return design

    def create_randomized_block_design(self, treatments: List[str],
                                      blocks: int = 4) -> Dict[str, Any]:
        """Create randomized block design"""
        import random

        design = {
            "type": "randomized_block",
            "treatments": treatments,
            "blocks": blocks,
            "assignments": []
        }

        for block in range(blocks):
            random_treatments = treatments.copy()
            random.shuffle(random_treatments)
            design["assignments"].append({
                "block": block,
                "treatments": random_treatments
            })

        return design

    def calculate_sample_size(self, effect_size: float, alpha: float = 0.05,
                             power: float = 0.8) -> int:
        """Calculate required sample size"""
        from scipy import stats

        # Two-sample t-test
        z_alpha = stats.norm.ppf(1 - alpha / 2)
        z_beta = stats.norm.ppf(power)

        n = 2 * ((z_alpha + z_beta) / effect_size) ** 2

        return int(np.ceil(n))


class DataCollector:
    """Data collection tools"""

    def __init__(self):
        self.datasets: Dict[str, List[Dict[str, Any]]] = {}
        self.schemas: Dict[str, Dict[str, str]] = {}

    def define_schema(self, name: str, schema: Dict[str, str]):
        """Define data schema"""
        self.schemas[name] = schema

    def collect_data(self, dataset: str, data: Dict[str, Any]):
        """Collect data point"""
        if dataset not in self.datasets:
            self.datasets[dataset] = []

        # Validate against schema
        if dataset in self.schemas:
            schema = self.schemas[dataset]
            for key, dtype in schema.items():
                if key not in data:
                    raise ValueError(f"Missing required field: {key}")

                if dtype == "int" and not isinstance(data[key], int):
                    raise ValueError(f"Field {key} must be int")
                elif dtype == "float" and not isinstance(data[key], (int, float)):
                    raise ValueError(f"Field {key} must be float")

        self.datasets[dataset].append(data)

    def get_dataset(self, name: str) -> List[Dict[str, Any]]:
        """Get dataset"""
        return self.datasets.get(name, [])

    def export_csv(self, dataset: str, filepath: str):
        """Export dataset to CSV"""
        import csv

        if dataset not in self.datasets:
            raise ValueError(f"Dataset {dataset} not found")

        data = self.datasets[dataset]
        if not data:
            return

        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)

    def import_csv(self, filepath: str, dataset: str):
        """Import dataset from CSV"""
        import csv

        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert strings to appropriate types
                converted = {}
                for key, value in row.items():
                    try:
                        converted[key] = float(value)
                    except ValueError:
                        converted[key] = value

                self.collect_data(dataset, converted)


class StatisticalAnalysis:
    """Statistical analysis for research"""

    @staticmethod
    def t_test(group1: List[float], group2: List[float]) -> Dict[str, float]:
        """Independent samples t-test"""
        from scipy import stats

        t_stat, p_value = stats.ttest_ind(group1, group2)

        return {
            "t_statistic": t_stat,
            "p_value": p_value,
            "significant": p_value < 0.05
        }

    @staticmethod
    def anova(*groups: List[float]) -> Dict[str, float]:
        """One-way ANOVA"""
        from scipy import stats

        f_stat, p_value = stats.f_oneway(*groups)

        return {
            "f_statistic": f_stat,
            "p_value": p_value,
            "significant": p_value < 0.05
        }

    @staticmethod
    def correlation(x: List[float], y: List[float]) -> Dict[str, float]:
        """Pearson correlation"""
        from scipy import stats

        corr, p_value = stats.pearsonr(x, y)

        return {
            "correlation": corr,
            "p_value": p_value,
            "significant": p_value < 0.05
        }

    @staticmethod
    def regression(x: List[float], y: List[float]) -> Dict[str, float]:
        """Linear regression"""
        from scipy import stats

        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

        return {
            "slope": slope,
            "intercept": intercept,
            "r_squared": r_value ** 2,
            "p_value": p_value,
            "std_error": std_err
        }


class ReproducibilityManager:
    """Reproducibility tools"""

    def __init__(self):
        self.environments: Dict[str, Dict[str, Any]] = {}
        self.dependencies: Dict[str, List[str]] = {}

    def capture_environment(self, name: str):
        """Capture computational environment"""
        import sys
        import platform

        self.environments[name] = {
            "python_version": sys.version,
            "platform": platform.platform(),
            "architecture": platform.architecture(),
            "timestamp": datetime.now().isoformat()
        }

    def record_dependencies(self, name: str, packages: List[str]):
        """Record package dependencies"""
        self.dependencies[name] = packages

    def generate_requirements(self, name: str) -> str:
        """Generate requirements.txt"""
        if name not in self.dependencies:
            return ""

        return "\n".join(self.dependencies[name])

    def export_environment(self, name: str, filepath: str):
        """Export environment specification"""
        import yaml

        env = {
            "environment": self.environments.get(name, {}),
            "dependencies": self.dependencies.get(name, [])
        }

        with open(filepath, 'w') as f:
            yaml.dump(env, f)


class PublicationManager:
    """Publication management"""

    def __init__(self):
        self.publications: Dict[str, Publication] = {}
        self.journals: List[str] = []

    def create_publication(self, title: str, authors: List[str]) -> Publication:
        """Create new publication"""
        pub = Publication(title=title, authors=authors)
        self.publications[pub.id] = pub
        return pub

    def add_journal(self, name: str):
        """Add journal to list"""
        self.journals.append(name)

    def generate_latex(self, publication: Publication) -> str:
        """Generate LaTeX for publication"""
        latex = f"""
\\documentclass{{article}}

\\title{{{publication.title}}}
\\author{{{', '.join(publication.authors)}}}
\\date{{\\today}}

\\begin{{document}}

\\maketitle

\\begin{{abstract}}
{publication.abstract}
\\end{{abstract}}

\\section{{Introduction}}
{publication.content}

\\end{{document}}
"""
        return latex

    def generate_bibtex(self, publication: Publication) -> str:
        """Generate BibTeX entry"""
        year = datetime.now().year
        bibtex = f"""@article{{{publication.id.replace('-', '')}},
  title={{{{{publication.title}}}}},
  author={{{{{', '.join(publication.authors)}}}},
  year={{{year}}},
  note={{Draft}}
}}
"""
        return bibtex


class CollaborationTools:
    """Research collaboration tools"""

    def __init__(self):
        self.collaborators: Dict[str, Dict[str, Any]] = {}
        self.permissions: Dict[str, Dict[str, List[str]]] = {}

    def add_collaborator(self, user_id: str, name: str, email: str, role: str = "contributor"):
        """Add collaborator"""
        self.collaborators[user_id] = {
            "name": name,
            "email": email,
            "role": role,
            "joined_at": datetime.now().isoformat()
        }

    def set_permissions(self, resource_id: str, user_id: str, permissions: List[str]):
        """Set permissions for user on resource"""
        if resource_id not in self.permissions:
            self.permissions[resource_id] = {}

        self.permissions[resource_id][user_id] = permissions

    def check_permission(self, resource_id: str, user_id: str, permission: str) -> bool:
        """Check if user has permission"""
        if resource_id not in self.permissions:
            return False

        if user_id not in self.permissions[resource_id]:
            return False

        return permission in self.permissions[resource_id][user_id]

    def get_activity_log(self, resource_id: str) -> List[Dict[str, Any]]:
        """Get activity log for resource"""
        # Simplified - would use actual logging in practice
        return []


class ExperimentManager:
    """Experiment management"""

    def __init__(self):
        self.experiments: Dict[str, Experiment] = {}
        self.current_experiment: Optional[Experiment] = None

    def create_experiment(self, name: str, description: str = "") -> Experiment:
        """Create new experiment"""
        exp = Experiment(name=name, description=description)
        self.experiments[exp.id] = exp
        self.current_experiment = exp
        return exp

    def load_experiment(self, exp_id: str) -> Optional[Experiment]:
        """Load experiment by ID"""
        return self.experiments.get(exp_id)

    def save_experiment(self, exp_id: str, filepath: str):
        """Save experiment to file"""
        exp = self.experiments.get(exp_id)
        if not exp:
            raise ValueError(f"Experiment {exp_id} not found")

        with open(filepath, 'w') as f:
            json.dump({
                "id": exp.id,
                "name": exp.name,
                "description": exp.description,
                "status": exp.status.value,
                "hypotheses": exp.hypotheses,
                "variables": exp.variables,
                "data": exp.data,
                "results": exp.results,
                "metadata": exp.metadata,
                "created_at": exp.created_at.isoformat(),
                "updated_at": exp.updated_at.isoformat()
            }, f, indent=2)

    def load_from_file(self, filepath: str) -> Experiment:
        """Load experiment from file"""
        with open(filepath, 'r') as f:
            data = json.load(f)

        exp = Experiment(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            status=ExperimentStatus(data.get("status", "planning")),
            hypotheses=data.get("hypotheses", []),
            variables=data.get("variables", {}),
            data=data.get("data", {}),
            results=data.get("results", {}),
            metadata=data.get("metadata", {})
        )
        exp.created_at = datetime.fromisoformat(data["created_at"])
        exp.updated_at = datetime.fromisoformat(data["updated_at"])

        self.experiments[exp.id] = exp
        return exp

    def run_experiment(self, exp_id: str, procedure: Callable) -> Dict[str, Any]:
        """Run experiment"""
        exp = self.experiments.get(exp_id)
        if not exp:
            raise ValueError(f"Experiment {exp_id} not found")

        exp.status = ExperimentStatus.RUNNING
        exp.updated_at = datetime.now()

        try:
            results = procedure(exp)
            exp.results = results
            exp.status = ExperimentStatus.COMPLETED
        except Exception as e:
            exp.status = ExperimentStatus.FAILED
            exp.results = {"error": str(e)}

        exp.updated_at = datetime.now()
        return exp.results


def create_experiment(name: str = "experiment") -> Experiment:
    """Create experiment"""
    return Experiment(name=name)


def main():
    """Main entry point for testing"""
    print("Testing Research Tools...")

    # Test Experimental Design
    ed = ExperimentalDesign()
    factorial_design = ed.create_factorial_design({
        "factor_A": [1, 2],
        "factor_B": ["low", "high"]
    })
    print(f"Factorial design: {factorial_design['num_treatments']} treatments")

    sample_size = ed.calculate_sample_size(effect_size=0.5)
    print(f"Sample size: {sample_size}")

    # Test Data Collector
    dc = DataCollector()
    dc.define_schema("measurements", {"value": "float", "unit": "str"})
    dc.collect_data("measurements", {"value": 10.5, "unit": "cm"})
    dc.collect_data("measurements", {"value": 12.3, "unit": "cm"})
    print(f"Dataset: {len(dc.get_dataset('measurements'))} points")

    # Test Statistical Analysis
    sa = StatisticalAnalysis()
    t_result = sa.t_test([1, 2, 3], [2, 3, 4])
    print(f"T-test: p={t_result['p_value']:.4f}")

    # Test Reproducibility Manager
    rm = ReproducibilityManager()
    rm.capture_environment("test")
    rm.record_dependencies("test", ["numpy", "scipy"])
    requirements = rm.generate_requirements("test")
    print(f"Requirements: {len(requirements.split())} characters")

    # Test Publication Manager
    pm = PublicationManager()
    pub = pm.create_publication("Test Paper", ["Author 1", "Author 2"])
    pub.abstract = "This is a test abstract."
    pub.content = "This is the content."
    latex = pm.generate_latex(pub)
    print(f"LaTeX: {len(latex)} characters")

    # Test Collaboration Tools
    ct = CollaborationTools()
    ct.add_collaborator("user1", "Alice", "alice@example.com", "author")
    ct.set_permissions("exp1", "user1", ["read", "write"])
    has_perm = ct.check_permission("exp1", "user1", "read")
    print(f"Has permission: {has_perm}")

    # Test Experiment Manager
    em = ExperimentManager()
    exp = em.create_experiment("Test Experiment", "A test experiment")
    em.save_experiment(exp.id, "test_experiment.json")
    loaded = em.load_from_file("test_experiment.json")
    print(f"Loaded experiment: {loaded.name}")

    print("\nResearch Tools initialized successfully")


if __name__ == "__main__":
    main()
