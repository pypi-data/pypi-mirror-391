use pyo3::prelude::*;

/// Fast computation in Rust
#[pyfunction]
fn compute_internal(data: Vec<f64>) -> PyResult<f64> {
    // Your Rust implementation
    Ok(data.iter().sum())
}

/// A private Python module implemented in Rust
#[pymodule]
#[pyo3(name = "_bima")] // Name must match Cargo.toml
fn _bima(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(compute_internal, m)?)?;
    m.add_class::<PyDataProcessor>()?;
    Ok(())
}

/// Example Rust struct exposed to Python
#[pyclass]
struct PyDataProcessor {
    inner: DataProcessor,
}

#[pymethods]
impl PyDataProcessor {
    #[new]
    fn new() -> Self {
        Self {
            inner: DataProcessor::new(),
        }
    }

    fn process(&self, data: Vec<f64>) -> PyResult<Vec<f64>> {
        Ok(self.inner.process(data))
    }
}

// Your actual Rust implementation (not exposed directly)
struct DataProcessor;
impl DataProcessor {
    fn new() -> Self {
        DataProcessor
    }
    fn process(&self, data: Vec<f64>) -> Vec<f64> {
        data
    }
}
