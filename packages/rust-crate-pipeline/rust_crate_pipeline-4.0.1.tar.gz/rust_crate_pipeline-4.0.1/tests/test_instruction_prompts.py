import json
from pathlib import Path

import pytest

from generate_teaching_bundles import TeachingBundleGenerator


SNIPPETS = {
    "async_module": """
pub mod api {
    use tokio::time::{sleep, Duration};

    pub struct User {
        pub id: u64,
        pub name: String,
    }

    pub async fn fetch_user(id: u64) -> Result<User, anyhow::Error> {
        sleep(Duration::from_millis(25)).await;
        Ok(User { id, name: format!("user-{id}") })
    }
}
""",
    "trait_impl": """
pub trait Greeter {
    fn greet(&self) -> String;
}

pub struct Console;

impl Greeter for Console {
    fn greet(&self) -> String {
        "hello".to_string()
    }
}
""",
    "serde_loader": """
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Debug)]
pub struct Config {
    pub host: String,
    pub port: u16,
}

impl Config {
    pub fn to_url(&self) -> String {
        format!("{}:{}", self.host, self.port)
    }
}

pub fn load_config(input: &str) -> Result<Config, anyhow::Error> {
    let cfg: Config = toml::from_str(input)?;
    Ok(cfg)
}
""",
}

SNAPSHOT_PATH = Path(__file__).parent / "snapshots" / "instruction_prompts.json"


@pytest.mark.parametrize("name", sorted(SNIPPETS))
def test_snapshot_inputs_are_valid_rust(name: str):
    """Basic sanity check to ensure snippets parse before snapshot comparison."""

    generator = TeachingBundleGenerator(
        output_dir=Path("/tmp"),
        pipeline_config={"instruction_llm": {"enabled": False}},
    )
    context = generator._parse_rust_context(SNIPPETS[name])
    assert context is not None, f"Failed to parse snippet {name}"


def test_instruction_prompt_snapshot(tmp_path: Path):
    generator = TeachingBundleGenerator(
        output_dir=tmp_path,
        pipeline_config={"instruction_llm": {"enabled": False}},
    )

    computed = {}
    for name, code in SNIPPETS.items():
        crate_name = f"{name}_crate"
        computed[name] = {
            "legacy": TeachingBundleGenerator._legacy_instruction_from_code(
                code, crate_name
            ),
            "modern": generator._create_instruction_from_code(code, crate_name),
        }

    if not SNAPSHOT_PATH.exists():
        SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
        SNAPSHOT_PATH.write_text(json.dumps(computed, indent=2, ensure_ascii=False), encoding="utf-8")
        pytest.fail(
            "Snapshot file created. Review and commit tests/snapshots/instruction_prompts.json."
        )

    expected = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    assert computed == expected
