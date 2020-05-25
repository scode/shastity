use std::collections::HashMap;

/// A simple in-memory hash map based store for purposes of testing.
#[derive(Default)]
pub struct MemWeakStore {
    map: HashMap<String, Vec<u8>>,
}

impl MemWeakStore {
    pub fn new() -> MemWeakStore {
        MemWeakStore {
            map: HashMap::new(),
        }
    }
}

impl super::WeakStore for MemWeakStore {
    fn weak_get(&mut self, key: &super::Key) -> Result<Option<Vec<u8>>, super::StoreError> {
        Ok(self.map.get(key.as_str()).map(|v| v.to_vec()))
    }

    fn weak_put(&mut self, key: &super::Key, value: &[u8]) -> Result<(), super::StoreError> {
        self.map.insert(key.as_str().to_owned(), value.to_owned());
        Ok(())
    }

    fn weak_exists(&mut self, key: &super::Key) -> Result<bool, super::StoreError> {
        Ok(self.map.contains_key(key.as_str()))
    }

    fn weak_delete(&mut self, key: &super::Key) -> Result<(), super::StoreError> {
        self.map.remove(key.as_str());
        Ok(())
    }

    fn weak_iter(&mut self) -> Box<dyn Iterator<Item = Result<super::Key, super::StoreError>>> {
        unimplemented!()
    }
}
