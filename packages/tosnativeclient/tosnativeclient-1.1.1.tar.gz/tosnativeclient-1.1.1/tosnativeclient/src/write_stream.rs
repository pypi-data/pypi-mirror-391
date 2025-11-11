use crate::tos_error::map_tos_error;
use pyo3::{pyclass, pymethods, PyRefMut, PyResult};
use std::sync::Arc;

const DEFAULT_PART_SIZE: isize = 8 * 1024 * 1024;
const DEFAULT_ONE_REQUEST_WRITE_BUFFER_LIMIT: isize = 50 * 1024 * 1024;
const DEFAULT_UPLOAD_PART_CONCURRENCY: isize = 20;
const MAX_UPLOAD_PART_SIZE: isize = 5 * 1024 * 1024 * 1024;
const MAX_PART_NUMBER: isize = 10000;
const OTHER_MU_KICK_OFF: i8 = 1;
const RELEASE_MU_KICK_OFF: i8 = 2;

#[pyclass(name = "WriteStream", module = "tosnativeclient")]
pub struct WriteStream {
    pub(crate) write_stream: Arc<tosnativeclient_core::write_stream::WriteStream>,
    #[pyo3(get)]
    pub(crate) bucket: String,
    #[pyo3(get)]
    pub(crate) key: String,
    #[pyo3(get)]
    pub(crate) storage_class: Option<String>,
}

#[pymethods]
impl WriteStream {
    pub fn write(slf: PyRefMut<'_, Self>, data: &[u8]) -> PyResult<isize> {
        let write_stream = slf.write_stream.clone();
        match slf.py().allow_threads(|| write_stream.write(data)) {
            Err(ex) => Err(map_tos_error(ex)),
            Ok(written) => Ok(written),
        }
    }

    pub fn close(slf: PyRefMut<'_, Self>) -> PyResult<()> {
        let write_stream = slf.write_stream.clone();
        match slf.py().allow_threads(|| write_stream.close()) {
            Err(ex) => Err(map_tos_error(ex)),
            Ok(_) => Ok(()),
        }
    }
}
