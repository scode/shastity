use std::error::Error;
use std::fmt;

// TODO(scode): Distinguish transient from permanent.
#[derive(Debug)]
pub struct StoreError {
}

impl Error for StoreError {
    fn description(&self) -> &str {
        unimplemented!()
    }

    fn cause(&self) -> Option<&Error> {
        unimplemented!()
    }
}

impl fmt::Display for StoreError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        unimplemented!()
    }
}

/// Provides storage of key->value mappings of reasonable size with weakend semantics sufficient for
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
/// for their use ase.
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
/// despite not yet being visible to readers.
///
/// Similarly, weak_exists() may also fail to return true despite an objecte having been previously
/// stored so long as it eventually becomes visible.
///
/// # Deletions and its complications
///
/// TODO(scode): Talk about races, including ts based cr, discovery and difficulty completely
/// deleting.
pub trait WeakStore {
    /// Get an object associated with the given key.
    ///
    /// # Return value
    ///
    /// Ok(Some(x)) on success and the value exists.
    ///
    /// Ok(None) indicates the value does not exist, or it has not yet become readable.
    fn weak_get(key: &[u8]) -> Result<Option<Vec<u8>>, StoreError>;

    fn weak_put(key: &[u8], value: &[u8]) -> Result<(), StoreError>;

    /// Determine whether a given key is associated with a value in the store.
    fn weak_exists(key: &[u8]) -> Result<bool, StoreError>;

    fn weak_delete(key: &[u8]) -> Result<(), StoreError>;
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
    fn get(key: &[u8]) -> Result<Option<Vec<u8>>, StoreError>;

    /// Put a value in the store regardless of whether there currently exists a value associated
    /// with the same key. Any existing value is overwritten.
    fn put(key: &[u8], value: &[u8]) -> Result<(), StoreError>;

    /// Put the given value into the store if and only if the current value associated with the
    /// key is expected_value (None means the value must be absent).
    fn put_if(key: &[u8], expected_value: Option<&[u8]>, new_value: &[u8]) -> Result<(), StoreError>;

    fn exists(key: &[u8]) -> Result<bool, StoreError>;
}
