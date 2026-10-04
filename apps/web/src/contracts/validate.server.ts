import Ajv2020, { type ErrorObject, type ValidateFunction } from "ajv/dist/2020";
import addFormats from "ajv-formats";
import { ContractViolationError } from "./errors";
import { contractPaths, readContractJson, type ContractSchemaKey } from "./schema-registry.server";

const ajv = new Ajv2020({ allErrors: true, strict: true });
addFormats(ajv);

const validators = new Map<ContractSchemaKey, ValidateFunction>();
const schemas = new Map(
  (Object.keys(contractPaths) as ContractSchemaKey[]).map((key) => [
    key,
    readContractJson(contractPaths[key]),
  ]),
);

for (const schema of schemas.values()) {
  if (typeof schema === "object" && schema !== null && "$id" in schema && typeof schema.$id === "string") {
    ajv.addSchema(schema);
  }
}

function validatorFor(key: ContractSchemaKey): ValidateFunction {
  const existing = validators.get(key);
  if (existing) return existing;
  const schema = schemas.get(key);
  if (schema === undefined) throw new Error(`Canonical contract schema is not registered: ${key}`);
  const schemaId = typeof schema === "object" && schema !== null && "$id" in schema ? schema.$id : undefined;
  const validator = typeof schemaId === "string" ? (ajv.getSchema(schemaId) ?? ajv.compile(schema)) : ajv.compile(schema);
  validators.set(key, validator);
  return validator;
}

function formatErrors(errors: ErrorObject[] | null | undefined): string {
  return (errors ?? [])
    .map((error) => `${error.instancePath || "/"} ${error.message ?? "is invalid"}`)
    .join("; ");
}

export function assertContract<T>(key: ContractSchemaKey, value: unknown): asserts value is T {
  const validator = validatorFor(key);
  if (!validator(value)) {
    throw new ContractViolationError(`Canonical ${key} contract validation failed: ${formatErrors(validator.errors)}`);
  }
}
