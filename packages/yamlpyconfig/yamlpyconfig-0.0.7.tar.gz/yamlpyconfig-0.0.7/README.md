# YAML Configuration Management: Local Files + Nacos Dynamic Configuration

This project provides a unified YAML configuration loading framework that supports both **local YAML files** and **Nacos configuration center**, with features such as hot updates, environment variable substitution, and encrypted value decoding.

Install the core package:

```bash
pip install yamlpyconfig
```

If you need Nacos support:

```bash
pip install yamlpyconfig[nacos]
```

---

# 1. Local YAML Configuration

Your configuration folder (e.g., `/config`) must contain at least:

* `application.yaml`
* Optional: `application-{profile}.yaml`

## 1.1 Profile Resolution Rules

The active profile is determined with the following priority (from highest to lowest):

1. Environment variable: `APP_PROFILE`
2. Environment variable: `SPRING_PROFILES_ACTIVE`
3. The `profile` field inside `application.yaml`
4. If none of the above exist → `application-{profile}.yaml` will NOT be loaded

### Notes

1. The configuration directory **must** contain `application.yaml`. Missing this file causes an error.
2. If a profile is resolved but `application-{profile}.yaml` does not exist, an exception is raised.

---

# 2. Loading Configuration from Nacos

To enable Nacos, declare the `config-sources.nacos` section inside your local configuration:

```yaml
config-sources:
  nacos:
    server-addr: "192.168.30.36:9090"
    namespace: "dev"
    group: "DEFAULT_GROUP"
    username: "nacos"
    password: "{encrypted}VuFvNZOg/q7ZQoIUGWydBw=="
    imports:
      - data-id: "gateway.yaml"
      - data-id: "application-ext.yaml"
```

## 2.1 Configuration Merge Priority (Low → High)

1. Local `application.yaml`
2. Local `application-{profile}.yaml`
3. Nacos imports (following the order declared; later entries override earlier ones)

---

# 3. Key Features and Usage Examples

## 3.1 Basic Usage

Example: load configuration and print updates automatically:

```python
@pytest.mark.asyncio
async def test_config_manager_with_nacos(self):
    async with ConfigManager("./") as config_manager:
        logger.info(config_manager.get_config())
        while True:
            await asyncio.sleep(5)
            logger.info(config_manager.get_config())
```

When entering the `async with` block:

* Local configuration is loaded first
* If Nacos is configured → it connects automatically and listens for real-time updates

---

## 3.2 Environment Variable Interpolation

Local YAML files support Spring-style placeholders:

```yaml
key-with-default: ${KEY1:DEFAULT_VALUE}
key: ${KEY2}
```

Behavior:

* If the environment variable exists → its value is used
* If it does not exist → use the default value after the colon
* If no default value is provided → `None` is returned

---

## 3.3 Encrypted Field Support (SM2 / SM4)

Sensitive fields (passwords, secret keys, etc.) can be encrypted and marked with the `{encrypted}` prefix:

```yaml
password: "{encrypted}VuFvNZOg/q7ZQoIUGWydBw=="
```

To enable automatic decryption, specify the algorithm and key when initializing `ConfigManager`:

```python
@pytest.mark.asyncio
async def test_config_manager_with_nacos_decrypt(self):

    # SM4 example — uses a symmetric key
    async with ConfigManager(
        "./",
        crypto_algorithm=AlgorithmEnum.SM4,
        key="lSU543Tes6wmjnb+PMVQNg=="
    ) as config_manager:

        logger.info(config_manager.get_config())
```

Explanation:

* **SM4** → symmetric encryption (pass the secret key)
* **SM2** → asymmetric encryption (provide the private key; public key optional depending on use case)
