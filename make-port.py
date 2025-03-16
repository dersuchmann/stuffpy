import fnvhash, sys
print(fnvhash.fnv1a_32(sys.argv[1].encode()) % 65535 + 1)
