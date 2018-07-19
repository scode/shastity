extern crate shastity;

use shastity::kv::mem;

mod weakstore;

#[test]
fn test() {
    weakstore::test_weak_get(&mut mem::MemWeakStore::new());
    weakstore::test_weak_put(&mut mem::MemWeakStore::new());
    weakstore::test_weak_exists(&mut mem::MemWeakStore::new());
    weakstore::test_weak_delete(&mut mem::MemWeakStore::new());
}
