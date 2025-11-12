# GPG Key Rotation Guide

Complete guide for rotating GPG keys in debrepomanager repositories with zero downtime.

## When to Rotate GPG Keys

- Key expiration approaching
- Security compromise or suspected compromise
- Regular security practice (annually recommended)
- Migrating to stronger key algorithm

## Quick Start

```bash
# 1. Verify new key
debrepomanager rotate-gpg-key --new-key-id NEWKEY123 --verify-only

# 2. Rotate with grace period
debrepomanager rotate-gpg-key --new-key-id NEWKEY123 --grace-period

# 3. Communicate to users (use client script)
curl -O https://repo.example.com/scripts/migrate-gpg-key.sh
chmod +x migrate-gpg-key.sh

# 4. After grace period, full rotation (optional)
debrepomanager rotate-gpg-key --new-key-id NEWKEY123
```

## Rotation Strategies

### Strategy 1: With Grace Period (Recommended)

Both old and new keys valid during transition.

```bash
debrepomanager rotate-gpg-key --new-key-id NEWKEY123 --grace-period
```

**Advantages:**
- Zero downtime
- Users can migrate gradually
- Safe rollback window

**Process:**
1. Rotate repositories with `--grace-period`
2. Publish new public key
3. Provide migration script to users
4. Wait 2-4 weeks for user migration
5. Optional: Final rotation without grace period

### Strategy 2: Immediate Rotation

New key only, immediate switch.

```bash
debrepomanager rotate-gpg-key --new-key-id NEWKEY123
```

**Use when:**
- Emergency (key compromise)
- Small user base
- Can coordinate with all users

## Step-by-Step Guide

### Preparation

1. **Generate new GPG key:**
```bash
gpg --full-generate-key
# Select RSA, 4096 bits
# Set expiration (2 years recommended)
```

2. **Import to server:**
```bash
gpg --import new-key.asc
gpg --list-keys  # Note the key ID
```

3. **Export public key for users:**
```bash
gpg --armor --export NEWKEY123 > /path/to/webroot/gpg/new-key.asc
```

### Execution

4. **Verify new key:**
```bash
debrepomanager rotate-gpg-key --new-key-id NEWKEY123 --verify-only
```

5. **Perform rotation:**
```bash
# With grace period
debrepomanager rotate-gpg-key --new-key-id NEWKEY123 --grace-period

# Or immediate
debrepomanager rotate-gpg-key --new-key-id NEWKEY123
```

6. **Verify rotation:**
```bash
# Check signature
aptly publish list
# All repositories should list new key
```

### Client Migration

7. **Provide migration script to users:**

Serve `scripts/migrate-gpg-key.sh` on your repository:

```bash
# On server
cp scripts/migrate-gpg-key.sh /path/to/webroot/scripts/
```

Users run:
```bash
curl https://repo.example.com/scripts/migrate-gpg-key.sh | sudo bash -s https://repo.example.com/gpg/new-key.asc OLDKEY123
```

## Rollback

If rotation fails or issues detected:

```bash
debrepomanager rotate-gpg-key --rollback --old-key-id OLDKEY456
```

**Prerequisites:**
- Old key still in keyring
- Old key not expired

## Grace Period Management

### During Grace Period

Both keys valid:
- Old clients continue working (old key)
- New clients use new key
- Gradual migration possible

### Ending Grace Period

After sufficient time (2-4 weeks):

```bash
# Optional: Remove old key from repositories
debrepomanager rotate-gpg-key --new-key-id NEWKEY123
```

## Troubleshooting

### "Key not found"
- Ensure key imported: `gpg --import key.asc`
- Check key ID: `gpg --list-keys`

### "Signing test failed"
- Test manually: `echo "test" | gpg --local-user KEYID --clear-sign`
- Check passphrase: GPG agent must be configured

### "Some repositories failed"
- Check logs for specific errors
- Rotate failed repos manually if needed
- Rollback if critical

## Client Migration Script

Location: `scripts/migrate-gpg-key.sh`

Features:
- Auto-detects system (Debian/Ubuntu/RedHat)
- Downloads new key
- Imports new key
- Removes old key (optional)
- Updates package lists
- Provides rollback instructions

## Security Best Practices

1. **Regular rotation:** Annually or bi-annually
2. **Strong keys:** RSA 4096 bits minimum
3. **Key expiration:** Set 2-3 years
4. **Grace period:** Use for production
5. **Communicate clearly:** Notify users in advance
6. **Test first:** Verify on test environment
7. **Backup:** Keep old key for rollback window

## See Also

- [CONFIG.md](CONFIG.md) - GPG configuration
- [QUICKSTART.md](QUICKSTART.md) - Basic GPG setup
- [ARCHITECTURE.md](ARCHITECTURE.md) - GPG integration architecture
