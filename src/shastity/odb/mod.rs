use std::fmt;
use std::error::Error;
use std::vec::Vec;

#[derive(Debug)]
pub struct OdbError<'a> {
    cause: Box<Error + 'a>
}


pub trait Odb {
    fn put(value: &[u8]) -> Box<Error>;
    fn get(value: &[u8]) -> Result<Vec<u8>, Box<Error>>;
}

impl<'a> Error for OdbError<'a> {
    fn description(&self) -> &str {
        // TODO: be useful
        "Generic OdbError"
    }

    fn cause(&self) -> Option<&Error> {
        Some(self.cause.as_ref())
    }
}

impl<'a> fmt::Display for OdbError<'a> {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        let success = write!(f, "OdbError: {}", self.description());
        match self.cause() {
            None => {
                success
            }
            Some(cause) => {
                try!(write!(f, "OdbError: {}", self.description()));
                fmt::Display::fmt(cause, f)
            }
        }
    }
}
