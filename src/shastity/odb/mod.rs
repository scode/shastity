use std::fmt;
use std::error::Error;
use std::vec::Vec;

#[derive(Debug)]
pub struct OdbError {
    cause: Option<Box<Error>>
}

pub trait Odb {
    fn put(value: &[u8]) -> Box<Error>;
    fn get(value: &[u8]) -> Result<Vec<u8>, Box<Error>>;
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
        try!(write!(f, "OdbError: {}", self.description()));
        match self.cause() {
            None => {
                Ok(())
            },
            Some(cause) => {
                try!(f.write_str(" caused by: "));
                fmt::Display::fmt(cause, f)
            }
        }
    }
}
