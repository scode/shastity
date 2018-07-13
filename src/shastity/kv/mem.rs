use kv;
use std::collections::HashMap;

/// A simple in-memory hash map based store for purposes of testing.
pub struct MemWeakStore {
    map: HashMap<Vec<u8>, Vec<u8>>,
}

impl MemWeakStore {
    pub fn new() -> MemWeakStore {
        MemWeakStore {
            map: HashMap::new(),
        }
    }
}


impl<'a> kv::WeakStore<'a> for MemWeakStore {
    fn weak_get(&mut self, key: &[u8]) -> Result<Option<Vec<u8>>, kv::StoreError> {
        Ok(self.map.get(key).map(|v| v.to_vec()))
    }

    fn weak_put(&mut self, key: &[u8], value: &[u8]) -> Result<(), kv::StoreError> {
        unimplemented!()
    }

    fn weak_exists(&mut self, key: &[u8]) -> Result<bool, kv::StoreError> {
        unimplemented!()
    }

    fn weak_delete(&mut self, key: &[u8]) -> Result<(), kv::StoreError> {
        unimplemented!()
    }

    fn weak_iter(&mut self) -> Result<&'a Iterator<Item = [u8]>, kv::StoreError> {
        unimplemented!()
    }
}
