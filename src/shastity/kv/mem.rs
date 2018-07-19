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
        self.map.insert(key.to_owned(), value.to_owned());
        Ok(())
    }

    fn weak_exists(&mut self, key: &[u8]) -> Result<bool, kv::StoreError> {
        Ok(self.map.contains_key(key))
    }

    fn weak_delete(&mut self, key: &[u8]) -> Result<(), kv::StoreError> {
        self.map.remove(key);
        Ok(())
    }

    fn weak_iter(&mut self) -> Result<&'a Iterator<Item = [u8]>, kv::StoreError> {
        unimplemented!()
    }
}
