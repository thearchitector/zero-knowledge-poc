TGF asset security. TGF zero-knowedge model (server never knows the data)

every user has an asymmetric key pair

- 'public_encryption_key' in database

1. password --> PBKDF2 --> private key
   -> supported in browser by web crypto api
   -> better with low entropy inputs (passwords)
2. private key --> Ed25519PrivateKey.from_private_bytes
   3 edpkey.public_key() --> public key --> db 'public_encryption_key'

---

**for group encryption to work, every user in a group needs to be able to derive the symmetric key of the group. they will use that key to view and encrypt group data.**

---

1. user creates a group. a symmetric key is generated. it is encrypted with the user's public key and stored on the the 'grouping' between the user and the new group.

- 'group_encryption_key' in db. this is ok because the user's key is asymmetric. the server cannot decrypt the group's encryption key without the host's private key, which is only ever derived & stored in browser as a cookie.

2. host/admin invites another user. when confirmed, host/admin decrypts the 'group*encryption_key' on their grouping and and encrypts it with the public key of the user. this is the 'group_encryption_key' stored on the grouping of the new member. .... this only works if the host/admin is the last person to take an action. it would require \_another* notification on the host side to "confirm" the "acceptance" (💀)

3. when a user wants to load items, they pull the 'group_encryption_key' from the grouping, decrypt it with their private key, then use it to decrypt the item data coming from the api.

4. when a user wants to share an item ...... this does not work because the ownership is with the "group". it doesn't permit sharing a single item with multiple groups unless the item is duplicated (💀)

---

**items themselves must be in control of permissions. items give read/write permissions to users. groups are only "groups" of users / arbitrary.**

---

1. user creates an item: a symmetric key is generated and encrypted with the user's public key and stored on a 'sharing' (new concept).

- 'sharing' is a new table mapping a user id, item id, and 'item_encryption_key'.
- 'item_encryption_key' in the db. this is ok because the user's key is asymmetric. the server cannot decrypt the item's encryption key without the user's private key, which is only ever derived & stored in browser as a cookie.

2. user shares an item with a group: the item's encryption key is decrypted with the user's private key (in browser). a new 'sharing' is created for every user in the group with the item's key encrypted with the public key of each user. the status of the sharing is `ACTIVE`.

- this has 1 huge downside. it is an extremely expensive operation (possibly prohibitively so).

3. a user views an item: check if can view. then pull the 'sharing'. the user (in browser) can then decrypt the item's data using their private key.

4. user updates an item: just decrypt, edit, and reencrypt the item data using the item's encryption key [decrypted with the user's private key].

5. user is added to a group: the inviter decrypts the private key of the group and encrypts it with the public key of the user. a 'sharing' is created with status `INACTIVE`. when the user accepts the group invite, the status of the sharing is set to `ACTIVE`.

- this has 1 huge downside. the item is technically "shared" regardless of whether or not the user has accepted the group invite.

6. if a user is removed from a group, their 'sharing' is deleted (or set to `INACTIVE` with the 'item_encryption_key' nullified).

---

**group operations may be very very very expensive for items shared with huge groups (Human, Community). the protocol cannot grow linearly with group size. sharing an item with a group should only involve the group's key. adding a user to a group should only involve the group's key. groups must serve as the proxy between a user and an item.**

---

1. user creates a group. a symmetric key is generated (browser side). an ephemeral key pair is generated. the symmetric key is encrypted with the user's public key and the ephemeral private key. both the encrypted key and the ephemeral public key are stored on a 'grouping' between the user and the new group.

- 'grouping' in the db maps a user id, group id, and 'group_encryption_key'.
- 'group_encryption_key' in db. this is ok because the user's key is asymmetric. the server cannot decrypt the group's encryption key without the user's private key, which is only ever derived & stored in browser.
- 'ephemeral_public_key'

3. host/admin invites another user to a group. the inviter decrypts the key of the group (via their own 'grouping') and encrypts it with the public key of the user. a 'grouping' is created with status `INACTIVE` and with the new encrypted key. when the user accepts the group invite, the status is set to `ACTIVE`. the invited user has access to the group's private key via their own 'grouping'.

- 1 huge downside: cryptographically, the user is a part of the group. the only barrier here is an app-imposed one ('grouping' "status").

8. user is removed from a group. delete the 'grouping' between the group and the user (or set it to `INACTIVE` and nullify the 'group_encryption_key').

9. user creates an item: a symmetric key is generated (browser side). the item's data is encrypted using it. the key is encrypted with the user's private group's key and stored on a 'sharing' (new concept) between the item and the user's private group.

- 'sharing' is a new table mapping a group id, item id, and 'item_encryption_key'.
- 'item_encryption_key' in the db. ok because there is no private data.

4. user shares an item with a group. user pulls the 'grouping' of themself and the current group. they decode the group's key using their own private key (in browser). user pulls the 'sharing' of that item and the current group and decodes the item's key using their decoded group key. a new 'sharing' is created using the item's key encoded with the new group's key.

5. user views an item. user pulls their 'grouping'. if doesn't exist or is not `ACTIVE`, 403. if ok, user decodes the group's key using their own private key. they pull the item's 'sharing' and decode the item's key using the group's key. they decode the item using the item's key.

6. user edits an item. the same steps as above, but they re-encrypt the item using the item's private key before sending to the api.

7. user unshares an item with a group. delete the 'sharing' between the item and the group (or set it to `INACTIVE` and nullify the 'item_encryption_key').
