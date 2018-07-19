extern crate shastity;

use shastity::kv::mem;

mod weakstore;

#[test]
fn test() {
    weakstore::test_get(&mut mem::MemWeakStore::new());
    weakstore::test_put(&mut mem::MemWeakStore::new());
    weakstore::test_exists(&mut mem::MemWeakStore::new());
}
