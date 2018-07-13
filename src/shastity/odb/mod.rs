use std::error::Error;
use std::fmt;
use std::vec::Vec;

pub struct Oid(String);
pub struct Content(Vec<u8>);

#[derive(Debug)]
pub struct OdbError {
    cause: Option<Box<Error>>,
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
///   - If two objects have the same id, they are identical. Thus,
///     two objects can be compared for equality without pulling the
///     content out of the store.
///   - Once an object is recorded in the store, it does not go away
///     unless explicit removal if requested through some means beyond
///     the scope of this trait. In other words, puts are durable.
///     For example, a local file system store would probably need to
///     fsync() prior to returning. (Exact semantics are up to implementation
///     and user configuration.)
///   - Callers cannot construct oids other than by giving the store the contents
///     to associate with the oid.
pub trait Odb {
    fn identify_object(content: &Content) -> Result<Oid, Box<Error>>;
    fn put_object(content: &Content) -> Result<Oid, Box<Error>>;
    fn get_object(oid: &Oid) -> Result<Content, Box<Error>>;
}

impl Error for OdbError {
    fn description(&self) -> &str {
        // TODO: be useful
        "Generic OdbError"
    }

    fn cause(&self) -> Option<&Error> {
        self.cause.as_ref().map(|c| &**c)
    }
}

impl fmt::Display for OdbError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "OdbError: {}", self.description())?;
        match self.cause() {
            None => Ok(()),
            Some(cause) => {
                f.write_str(" caused by: ")?;
                fmt::Display::fmt(cause, f)
            }
        }
    }
}
