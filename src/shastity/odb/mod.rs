use std::error::Error;
use std::fmt;
use std::vec::Vec;

#[derive(Debug)]
pub struct OdbError {
    cause: Option<Box<Error>>
}

/// A content addressable object database.
///
/// For information on the general concept of content addressable
/// storage, see:
///
///   https://en.wikipedia.org/wiki/Content-addressable_storage
///
/// Properties of an Odb include:
///
///   - If two objects have the same key, they are identical. Thus,
///     two objects can be compared for equality without pulling the
///     content out of the store.
///   - Once an object is recorded in the store, it does not go away
///     unless explicit removal if requested through some means beyond
///     the scope of this trait. In other words, puts are durable.
///     For example, a loacl file system store would probably need to
///     fsync() prior to returning. (This does not preclude e.g.
///     in memory implementation.)
///   - Keys can never be predicted by the caller. Only keys returned
///     from put() can be assumed to be valid.
///
/// Caveats:
///
///   - Batch based puts would allow for greater performance w/o
///     concurrency.
///   - No attempt is made to support very large objects (which would
///     complicate the interface). Chunking is recommended to be
///     performed on top.
///   - There is no provision for concurrent access at this time.
pub trait Odb {
    fn put(value: &[u8]) -> Result<Vec<u8>, Box<Error>>;
    fn get(key: &[u8]) -> Result<Vec<u8>, Box<Error>>;
}

impl Error for OdbError {
    fn description(&self) -> &str {
        // TODO: be useful
        "Generic OdbError"
    }

    fn cause(&self) -> Option<&Error> {
        self.cause.as_ref().map(|c| {
            &**c
        })
    }
}

impl fmt::Display for OdbError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "OdbError: {}", self.description())?;
        match self.cause() {
            None => {
                Ok(())
            },
            Some(cause) => {
                f.write_str(" caused by: ")?;
                fmt::Display::fmt(cause, f)
            }
        }
    }
}
