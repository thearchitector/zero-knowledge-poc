# zero-knowledge-poc

poc for testing a zero-knowledge group-based asset system for tgf

the application layer on the UI & BE are horribly slow and unoptimized.

the cryptographic model is higher fidelity / (nearly) production ready.

- users can login/be created
- users can create items
- users can see items shared with groups they're in
- users cannot see items shared with groups they're not in
- server can never see the item data, or any other private data, its encrypted
- users can share and unshare items from groups
  - after unsharing an item from a group, users in that group cannot view the item _even if_ they took note of the cryptographic keys used at the time of the initial viewing (forward secrecy)

copyright 2024 elias gabriel. not for redistribution or modification. all rights reserved.

## running

docker compose project. just `docker compose up --build` and go to `localhost:3000`.

## explanation

the fundamental principle here is that items are encrypted before upload, and that groups facilitate access to said items' encryption keys. items own their own data, so **additive** permission / authorization changes never necessitate re-encryption. access can be controlled entirely through the existence of individual "sharings" and "groupings".

<https://drive.google.com/file/d/1gSnLa0OlCV8gfHS4aRuWzdc2bIdGrZXo/view?usp=sharing>

<details>
<summary>transcript:</summary>

```
every user has an encryption key. they get a private and public key. their key is derived from their password in a cryptographically secure way

every user is the host of at least one group, their personal group. when a user is created, their group is created as well.

groups also have encryption keys.

when a user is added to a group, that relationship is stored in a "grouping". that grouping maps a user to a group, but ALSO contains a copy of the group's encryption key _encrypted_ using the user's public key.

when a user creates an item, the item also has an encryption key. the contents of the file are encrypted using that encryption key.

we want to ensure that every user in a group has access to items shared with that group; item's aren't shared directly with people, they're shared with groups.

when the item is created, it's encryption key is _encrypted_ using the creating user's personal group's private key. the user creating the item knows their personal group's private key because they can decrypt it from their grouping: take the encrypted key from the grouping and decrypt it with their own private key. this information is stored on a "sharing". a sharing maps a group to an item, and contains that copy of the item's encryption key that has been encrypted with the group's key.

when a user wants to view an item, they need 2 things:
1. a sharing
2. a grouping
the user needs to have some way of accessing the item's encryption key. ie, they need to have a grouping that maps their user to the group so that they can access the sharing that maps that group to the item. if they're not a part of the group, they don't have a grouping, and should be disallowed from trying to read a sharing.

once they have the sharing, reading an item means:
1. using their grouping, decrypt the group's private key using their own private key.
2. using the sharing, use the now decrypted group key and decrypt the item's private key.
3. download the gibberish/encrypted item contents, then decrypt them using the now decrypted item private key.

-----

permissions and management take the form of controlling groupings and sharings, and ensuring that only users who have a grouping can access the sharings associated with a group. permissions are not in scope for this POC, because they can exist _above_ the encryption/data model.

the model in the poc enables a core feature for TGF: actually private content. item content is encrypted before reaching our servers, and is stored encrypted. we _cannot_ know the contents of those items, and no other user can know the contents, unless we or said user are a part of a group with which the item is shared.

no sensitive information leaves the user's device. the only things transmitted to the BE are encrypted information and information that doesn't reveal any information (like the user's public key, which is distributable). practically, this means ALL cryptographic functions happen in the browser. they must.

-----

there are 2 users in the demo. user 1 created an item and it is shared with their personal group. user 2 created an item and it is shared with their personal group. user 1 can switch to their group and see the item they created, but cannot see the other item because they're not a part of user 2's private group (and therefore cannot get access to the sharing). vice versa for user 2 and their item.
```

</details>
