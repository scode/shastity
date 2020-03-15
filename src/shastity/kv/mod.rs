pub mod mem;

use std::error::Error;
use std::fmt;
use std::option::Option;

// TODO(scode): Distinguish transient from permanent.
#[derive(Debug)]
pub struct StoreError {}

impl Error for StoreError {
    fn source(&self) -> Option<&(dyn Error + 'static)> {
        unimplemented!()
    }

    fn description(&self) -> &str {
        unimplemented!()
    }
}

impl fmt::Display for StoreError {
    fn fmt(&self, _f: &mut fmt::Formatter) -> fmt::Result {
        unimplemented!()
    }
}

pub struct Cursor(Vec<u8>);

/// The result of an iteration step against a store.
pub struct IterationResult {
    /// If Some(x), a cursor to be used to continue the iteration. If None, indicates reaching the
    /// end of the iteration.
    _cursor: Option<Cursor>,

    /// The keys discovered at this step of the iteration. May be empty even if there is more
    /// iteration to be done. The cursor must be inspected to detect end-of-iteration.
    _keys: Vec<u8>,
}

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
/// * The "iteration process" refers to a sequence of calls to weak_iter() until the very end of
///   iteration has bene reached as communicated by the returned IterationResult.
/// * The store may be both written to and read from concurrently with an iteration process.
/// * Any object written to the store prior to the start of iteration must be visible in the
///   iteration *except* sa constrained by eventual consistency.
/// * An object written to the store during iteration *may* be visible to the iteration. If a
///   previously existing object is over-written, *either* the old or the new object must be
///   visible. The only exception is eventual consistency (should the old object not yet be
///   visible).
/// * Keys may be exposed through iteration in any order that suits the ipmlementation.
///
/// The presumption is that iteration may be a very long running process that spans even hours or
/// days on a large store.
///
/// There is currently no mechanism to allow concurrent iteration of a store.
pub trait WeakStore<'a> {
    /// Get an object associated with the given key.
    ///
    /// # Return value
    ///
    /// Ok(Some(x)) on success and the value exists.
    ///
    /// Ok(None) indicates the value does not exist, or it has not yet become readable.
    fn weak_get(&mut self, key: &[u8]) -> Result<Option<Vec<u8>>, StoreError>;

    fn weak_put(&mut self, key: &[u8], value: &[u8]) -> Result<(), StoreError>;

    /// Determine whether a given key is associated with a value in the store.
    fn weak_exists(&mut self, key: &[u8]) -> Result<bool, StoreError>;

    fn weak_delete(&mut self, key: &[u8]) -> Result<(), StoreError>;

    /// Perform an iteration step to discover keys in the store.
    ///
    /// If cursor is Some(x), it must be a cursor obtained by a previous invocation of this
    /// method.
    ///
    /// If cursor is None, iteration will start at the beginning.
    ///
    /// max_items indicates the maximum number of keys to return. The iteration may return
    /// any number of items equal to or less than that, including zero.
    ///
    /// See also: Iteration sectoin of class documentation.
    /// See also: Documentation of IterationResult.
    fn weak_iter(
        &mut self,
        cursor: Option<Cursor>,
        max_items: usize,
    ) -> Result<IterationResult, StoreError>;
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
    fn get(&mut self, key: &[u8]) -> Result<Option<Vec<u8>>, StoreError>;

    /// Put a value in the store regardless of whether there currently exists a value associated
    /// with the same key. Any existing value is overwritten.
    fn put(&mut self, key: &[u8], value: &[u8]) -> Result<(), StoreError>;

    /// Put the given value into the store if and only if the current value associated with the
    /// key is expected_value (None means the value must be absent).
    fn put_if(
        &mut self,
        key: &[u8],
        expected_value: Option<&[u8]>,
        new_value: &[u8],
    ) -> Result<(), StoreError>;

    fn exists(&mut self, key: &[u8]) -> Result<bool, StoreError>;
}
