"""Tests for the shared Rust code example quality heuristics."""

from rust_crate_pipeline.utils.code_example_quality import is_high_quality_example


def test_accepts_async_block_without_function():
    code = """
    use tokio::task;
    use tokio::time::{sleep, Duration};

    let handle = tokio::spawn(async move {
        sleep(Duration::from_millis(25)).await;
        println!("processing finished");
    });

    handle.await.unwrap();
    """

    assert is_high_quality_example(code)


def test_accepts_macro_definition_without_function():
    code = """
    #[macro_export]
    macro_rules! collect_pairs {
        ($($key:expr => $value:expr),+ $(,)?) => {{
            let mut map = std::collections::HashMap::new();
            $(map.insert($key, $value);)+
            map
        }};
    }
    """

    assert is_high_quality_example(code)


def test_accepts_trait_with_default_method():
    code = """
    pub trait Greeter {
        fn greet(&self, name: &str) -> String;

        fn greet_formally(&self, name: &str) -> String {
            format!("Greetings, {}", name)
        }
    }

    pub struct FriendlyGreeter;

    impl Greeter for FriendlyGreeter {
        fn greet(&self, name: &str) -> String {
            format!("Hello, {}", name)
        }
    }
    """

    assert is_high_quality_example(code)
