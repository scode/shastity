pub mod mem;

use std::error::Error;
use std::fmt;
use std::option::Option;

#[derive(Debug)]
pub struct StoreError {}

impl Error for StoreError {
    fn source(&self) -> Option<&(dyn Error + 'static)> {
        unimplemented!()
    }
}

impl fmt::Display for StoreError {
    fn fmt(&self, _f: &mut fmt::Formatter) -> fmt::Result {
        unimplemented!()
    }
}

/// The provided string was not a valid representation of a key.
#[derive(Debug)]
#[non_exhaustive]
pub enum InvalidKeyError {
    /// The provided string contained one or more disallowed characters.
    InvalidCharacter,

    /// The provided string was empty, which is not a valid key.
    Empty,
}

/// A key with which values can be assocaited in a store.
///
/// A key is a string guaranteed to be non-empty and contain only `[0-9a-f]`.
///
/// # Examples
///
/// ```
/// # use shastity::kv::Key;
/// let key = Key::new("abcd").unwrap();
/// let s = String::from(key);
/// ```
#[derive(Debug, Clone)]
pub struct Key {
    s: String,
}

impl Key {
    /// Construct a new key from the given string. Fails if the string contains disallowed
    /// characters, or is empty.
    ///
    /// ```
    /// # use shastity::kv::Key;
    /// assert_eq!(String::from(Key::new("abcdef").unwrap()), "abcdef");
    /// assert_eq!(String::from(Key::new("0123456789").unwrap()), "0123456789");
    /// assert!(Key::new("g").is_err());
    /// assert!(Key::new("").is_err());
    /// assert!(Key::new("BBCDEF").is_err());
    /// ```
    pub fn new<T: Into<String>>(k: T) -> Result<Self, InvalidKeyError> {
        let s = k.into();

        if s.is_empty() {
            return Err(InvalidKeyError::Empty);
        }

        for c in s.chars() {
            if !match c {
                '0'..='9' => true,
                'a'..='f' => true,
                _ => false,
            } {
                return Err(InvalidKeyError::InvalidCharacter);
            }
        }

        Ok(Key { s })
    }

    pub fn as_str(&self) -> &str {
        &self.s
    }
}

impl AsRef<str> for Key {
    fn as_ref(&self) -> &str {
        &self.s
    }
}

impl From<Key> for String {
    /// ```
    /// # use shastity::kv::Key;
    /// assert_eq!(String::from(Key::new("abcdef").unwrap()), "abcdef");
    /// ```
    fn from(k: Key) -> String {
        k.s
    }
}

impl From<&Key> for String {
    /// ```
    /// # use shastity::kv::Key;
    /// assert_eq!(String::from(Key::new("abcdef").unwrap()), "abcdef");
    /// ```
    fn from(k: &Key) -> String {
        String::from(&k.s)
    }
}

pub struct Cursor(Vec<u8>);

/// Provides storage of key->value mappings of reasonable size with weakened semantics sufficient for
/// use by a content addressable store, but maximally relaxed to allow implementation
/// flexibility and efficiency.
///
/// # Size restrictions
///
/// There is no specific restriction on size other than that which is implied by the fact that
/// both keys and values are assumed to be reasonable to keep on the heap and rapidly allocate
/// and de-allocate.
///
/// Real implementations will likely have some restrictions, but such restrictions are opaque
/// to the caller and the user is expected to select an appropriate implementation and configuration
/// for their use case.
///
/// # Storage semantics
///
/// A successful weak_put() must guarantee that the value has been durably stored. The exact definition
/// of durable is contextual on implementation and user requirements. For example, a local filesystem
/// implementation would likely use fsync() or similar mechanisms; a distributed storage system
/// would likely ensure multiple replicas have been written. The caller is not expected to
/// handle the case of an object being permanently lost unless it has been explicitly deleted.
///
/// A weak_put() in the presence of a pre-existing value associated with the same key is to be considered
/// successful. However, it is undefined whether the value is overwritten or the previously existing
/// value is kept. This is sufficient for usage in a content addressable storage context, and allows
/// a wide range of flexibility in implementation. For example, an eventually consistent distributed
/// storage system with timestamp based conflict resolution would satisfy this requirement (but see
/// section below on deletions).
///
/// A weak_put() must guarantee that the value has atomically been either written or not
/// written. Writes must never complete partially such that a future read will return truncated or
/// corrupt data - even if there is a pre-existing value in the store.
///
/// A weak_put() is allowed to succeed even though an immediately subsequent get() would not return the
/// newly written object (even in the absence of a deletion). Callers may, depending on context,
/// perform backoff and retries as appropriate to be resilient to eventual consistency in the store.
/// This is not in conflict with the durability requirement, as a value could be durably written
/// despite not yet being immediately visible to readers.
///
/// Similarly, weak_exists() may also fail to return true despite an objecte having been previously
/// stored so long as it eventually becomes visible.
///
/// weak_iter() iterates over all keys in the store, with semantics similar to weak_get(). A
/// complete iteration may fail to observe some items due to eventual consistency, but should
/// otherwise be complete. More on iteration below.
///
/// # Deletions and its complications
///
/// For the most part, the intention of this trait and its use is to allow for safe un-coordinated
/// access to the store by multiple processes. Uncoordinated insertion of duplicate values will
/// at worst result in unnecessary work, but not cause incorrectness.
///
/// Deletions present a coordination problem, however, because they introduce a dependency on the
/// order of operations. Typically, deletion would only happen if an object is no longer needed
/// due to not being referenced by any other object (this is very analogous to a garbage
/// collector), but the act of deleting an object will be fundamentally raceful with respect
/// to concurrent writers.
///
/// This problem is not solved here. Callers that rely on deletes, or are subject to deletes by
/// others, must solve that coordination problem separately.
///
/// # Iterating over keys in a store
///
/// A WeakStore does not provide any atomic view of the entries that exists in the store. Instead,
/// the process of iterating over keys is subject to the following contract:
///
/// * The store may be both written to and read from concurrently with an iteration process.
/// * Any object written to the store prior to the start of iteration must be visible in the
///   iteration *except* as constrained by eventual consistency.
/// * An object written to the store during iteration *may* be visible to the iteration. If a
///   previously existing object is over-written, *either* the old or the new object must be
///   visible. The only exception is eventual consistency (should the old object not yet be
///   visible).
/// * Keys may be exposed through iteration in any order that suits the implementation.
pub trait WeakStore {
    /// Get an object associated with the given key.
    ///
    /// # Return value
    ///
    /// Ok(Some(x)) on success and the value exists.
    ///
    /// Ok(None) indicates the value does not exist, or it has not yet become readable.
    fn weak_get(&mut self, key: &Key) -> Result<Option<Vec<u8>>, StoreError>;

    fn weak_put(&mut self, key: &Key, value: &[u8]) -> Result<(), StoreError>;

    /// Determine whether a given key is associated with a value in the store.
    fn weak_exists(&mut self, key: &Key) -> Result<bool, StoreError>;

    fn weak_delete(&mut self, key: &Key) -> Result<(), StoreError>;

    /// Provides an iterator over all keys in the store.
    ///
    /// Iteration is only successful if the iterator is finished *and* if all results
    /// consumed were Ok().
    ///
    /// TODO: This interface does not allow for resumption nor concurrency, it should.
    fn weak_iter(&mut self) -> Box<dyn Iterator<Item = Result<Key, StoreError>>>;
}

/// Provides storage of key->value mappings of reasonable size with strongly consistent semantics.
///
/// # Storage semantics
///
/// The result of a put_if() is guaranteed to be visible to a subsequent get() or exists().
///
/// put_if() is guaranteed to atomically put the new value provided only if the existing value
/// (present or absent) matches the provided expected value.
pub trait Store {
    fn get(&mut self, key: &Key) -> Result<Option<Vec<u8>>, StoreError>;

    /// Put a value in the store regardless of whether there currently exists a value associated
    /// with the same key. Any existing value is overwritten.
    fn put(&mut self, key: &Key, value: &[u8]) -> Result<(), StoreError>;

    /// Put the given value into the store if and only if the current value associated with the
    /// key is expected_value (None means the value must be absent).
    fn put_if(
        &mut self,
        key: &[u8],
        expected_value: Option<&[u8]>,
        new_value: &[u8],
    ) -> Result<(), StoreError>;

    fn exists(&mut self, key: &Key) -> Result<bool, StoreError>;
}
