extern crate shastity;

use shastity::kv::mem;

mod weakstore;

#[test]
fn test() {
    weakstore::test_get(&mut mem::MemWeakStore::new());
}
