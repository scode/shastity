package org.scode.shastity.java;

import java.util.Arrays;

/**
 * Bytes is a thin wrapper around a byte[] array which allows treating bytestrings as values, and avoids
 * accidentally leaking mutable state. The underlying byte[] is accessible by explicit request, so there is no
 * strict immutability enforced.
 */
public class Bytes {
    public static final Bytes EMPTY = new Bytes();

    private byte[] array;

    /**
     * Create an empty Bytes.
     */
    public Bytes() {
        this.array = new byte[0];
    }

    /**
     * Create a Bytes instance by copying the given byte[].
     *
     * @param bytes The byte[] to copy.
     */
    public Bytes(byte[] bytes) {
        this(bytes, true);
    }

    /**
     * Private constructor allowing copying or not. Not exposed because non-copying
     * construction should be terribly obivous in calling code.
     */
    private Bytes(byte[] bytes, boolean copy) {
        if (copy) {
            this.array = new byte[bytes.length];
            System.arraycopy(bytes, 0, this.array, 0, bytes.length);
        } else {
            this.array = array;
        }
    }

    /**
     * Construct a Bytes wrapping the given array, not doing any copying. Bytes will assume
     * that the caller is transfering complete ownership of the byte array and that the byte
     * array will never be modified by the caller.
     *
     * @param bytes The byte[] to be wrapped.
     * @return The newly constructed Bytes.
     */
    public static Bytes wrapArray(byte[] bytes) {
        return new Bytes(bytes, false);
    }

    public byte[] getMutableByteArray() {
        return this.array;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;

        Bytes bytes = (Bytes) o;

        if (!Arrays.equals(array, bytes.array)) return false;

        return true;
    }

    @Override
    public int hashCode() {
        return array != null ? Arrays.hashCode(array) : 0;
    }
}
