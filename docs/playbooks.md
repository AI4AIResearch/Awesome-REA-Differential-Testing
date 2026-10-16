# Reverse engineering workflows

Choose one question with a checkable answer. These are starting workflows derived from upstream documentation; the included [Electron lab](../labs/electron-notes/README.md) has a separate CLI execution receipt. The other workflows have not been executed by this collection.

## Game behavior

**Question:** Which calculation, asset relationship, or rendering step explains one visible behavior?

Choose the surface before choosing a tool. For native calculations, start with the REA [DX-Ball](https://rea.tools/showcase/dx-ball/) and [TH04](https://rea.tools/showcase/th04/) investigations. For Unity data, [AssetRipper](https://github.com/AssetRipper/AssetRipper) explores assets; [Cpp2IL](https://github.com/SamboyCoding/Cpp2IL) and [Il2CppDumper](https://github.com/Perfare/Il2CppDumper) have distinct IL2CPP recovery limits. These are independent companion tools, not asserted REA providers.

For graphics, [RenderDoc](https://github.com/baldurk/renderdoc) inspects frames from your own or supported open-source projects. The independent [RenderDoc MCP](https://github.com/scarletfantasy/renderdoc-mcp) exposes existing Windows captures to an agent. Use upstream capture and replay requirements.

```text
Limit the investigation to one calculation, asset relationship, or rendering
event. Identify the engine and artifact type. Cite addresses, metadata records,
or capture event IDs for each claim. Distinguish metadata recovery, method-code
reconstruction, and observed graphics state. Propose one independent check.
```

Deliver a small evidence-backed result. Dummy assemblies do not restore method implementations; a frame capture does not explain every gameplay system.

## Electron feature trace

**Question:** Which code path turns a UI action into an exported file?

Start with an extracted application directory or ASAR. REA's static JavaScript lane can map modules and application boundaries without a native decompiler. Save the full Evidence output, then use a bounded analysis view when it is large.

Give your agent this task:

```text
Trace this one feature from renderer entry point through preload and IPC to
the main-process handler and transformation. Cite each file and location.
Separate discovered edges from inferred edges. Explain what static analysis
cannot establish. Propose two inputs that would distinguish competing explanations.
```

Deliver a call path, evidence locations, and a small input/output check. Start with the [original Notes fixture](../labs/electron-notes/README.md). Sources: [JavaScript guide](https://rea.tools/guides/javascript/), [application workflows](https://github.com/morluto/rea/blob/main/docs/javascript-application-workflows.md).

## Native function recovery

**Question:** What does one bounded calculation do?

Choose a known binary format and a configured provider. Ghidra, Hopper, and IDA have different platform and licensing requirements. Begin with artifact identity, architecture, strings, imports, and cross-references; narrow to one function before reconstructing it.

```text
Identify the function relevant to this behavior. For each proposed variable,
type, and branch condition, cite the address and underlying instructions.
Use pseudocode as a reading aid. Report ambiguities in calling convention,
signedness, overflow, and external state. Design a small differential check.
```

Deliver the evidence-backed reconstruction and boundary cases. Do not claim source recovery or byte equivalence from readable pseudocode alone. Sources: [native guide](https://rea.tools/guides/native/), [native investigations](https://github.com/morluto/rea/blob/main/docs/native-investigation.md).

## Android APK

**Question:** Which class and method implement one app behavior?

Start with a local APK, a full JDK 17+, and the documented `jadx-headless-mcp` 0.7.1 integration. Record the APK hash, manifest facts, and exact class/method identifiers. Java/Kotlin code, native libraries, and JavaScript bundles are separate analysis surfaces.

```text
Map the entry points relevant to this feature, then follow only the necessary
classes and methods. Cite manifest declarations and decompiled locations.
Mark native calls, reflection, dynamically loaded code, and missing bodies
as boundaries. Do not infer runtime behavior solely from a manifest entry.
```

Deliver a bounded trace with unresolved edges. Sources: [Android analysis](https://github.com/morluto/rea/blob/main/docs/android-analysis.md), [Aegis worked case](https://rea.tools/showcase/aegis/).

## Dotnet assembly

**Question:** What does a selected type or method do in a managed assembly?

REA's managed lane reads PE/CLI metadata and CIL without executing the assembly. Inspect the actual deployment form first: a `.dll` extension does not prove a supported managed assembly, and NativeAOT or IL2CPP needs a different route.

```text
Identify this artifact's deployment form. List candidate types, select one
using its exact full name, and explain the method from CIL and metadata.
Distinguish declared native dependencies from observed runtime calls.
Record unsupported or undecoded parts rather than filling them in.
```

Deliver assembly identity, selected members, and instruction-backed findings. Source: [managed-code analysis](https://github.com/morluto/rea/blob/main/docs/managed-code-analysis.md).

## Saved network capture

**Question:** What request sequence implements a visible operation?

Use a sanitized local HAR or supported SAZ recording. Begin with request order, URLs, methods, response status, and available bodies. For packet-level work, choose the separate PCAP/TShark workflow and its documented host requirements.

```text
Explain this operation using only the saved capture. Cite the entry index,
request, response, and payload field supporting each step. Separate observed
ordering from inferred causality. Identify absent bodies, cached responses,
and encrypted or omitted content. Do not make new network requests.
```

Deliver a sequence and evidence references. A capture does not reveal server implementation. Sources: [web network captures](https://github.com/morluto/rea/blob/main/docs/web-network-captures.md), [packet captures](https://github.com/morluto/rea/blob/main/docs/packet-captures.md).

## Firmware image

**Question:** What regions and embedded files are present in this image?

Use a local image and the supported Binwalk or Unblob setup. The upstream workflow has Linux-specific requirements. Keep an extraction budget and record file offsets and hashes before following an embedded native binary into a separate provider.

```text
Inventory the image's regions and candidate embedded files. Cite offsets,
sizes, hashes, and the extraction tool. Separate a signature match from a
validated file. Bound recursive extraction and report truncation or errors.
Select one extracted artifact for a follow-up investigation.
```

Deliver an extraction map and a clear next target. Source: [firmware analysis](https://github.com/morluto/rea/blob/main/docs/firmware-analysis.md).
