# MyKOS — Development Roadmap

- Status: Proposed
- Initial target: Installable x86_64 desktop distribution
- Related: Product Vision and Architecture in this directory

## Delivery strategy

Develop in small, demonstrable milestones. Each milestone must produce a buildable or testable result with explicit acceptance criteria. Do not start broad custom desktop development before the base distribution can be reproduced, installed, and tested.

## M0 — Foundation and first boot

**Goal:** Produce the first reproducible MyKOS ISO using an established Ubuntu LTS base and KDE Plasma.

Work:
- Select and pin the Ubuntu LTS release.
- Choose and document the image build toolchain.
- Define the initial package manifest and repository sources.
- Configure KDE Plasma and basic MyKOS branding.
- Build an x86_64 ISO.
- Boot it in QEMU/KVM.
- Install to a clean virtual disk and verify first login.
- Record known issues and build instructions.

Acceptance:
- Build can be repeated from documented inputs.
- ISO boots in QEMU/KVM.
- Installation to a clean virtual disk succeeds.
- KDE Plasma starts and a user can log in.
- Network, audio, display, file manager, terminal, and package management pass basic smoke tests.
- Build metadata and checksums are produced.

## M1 — Desktop experience

**Goal:** Establish consistent visual and interaction defaults.

Work:
- Define visual identity, theme, iconography, typography, and wallpaper.
- Configure panel, launcher, notifications, shortcuts, and virtual desktops.
- Review accessibility and keyboard navigation.
- Document desktop configuration and reset behavior.

Acceptance:
- Consistent branding across login, desktop, and system settings.
- Common desktop tasks work without custom instructions.
- Configuration can be reproduced from source.

## M2 — System management

**Goal:** Make common system settings understandable and reliable.

Work:
- Evaluate existing KDE settings modules before writing replacements.
- Integrate display, network, Bluetooth, audio, power, storage, and user management.
- Add MyKOS-specific help, status, and diagnostics only where upstream UX is insufficient.
- Define permission boundaries for privileged operations.

Acceptance:
- Common settings workflows work on the supported hardware matrix.
- Privileged actions use supported authorization mechanisms.
- Errors are surfaced clearly and do not leave the system in an unknown state.

## M3 — Application experience

**Goal:** Provide a coherent application discovery and management workflow.

Work:
- Define trusted software sources and catalog metadata.
- Integrate Flatpak and the base package manager.
- Design install, update, uninstall, and permission UX.
- Show publisher/source and update ownership clearly.

Acceptance:
- Users can discover, install, launch, update, and remove supported applications.
- The UI accurately represents application source and permissions.
- Failed operations produce actionable errors.

## M4 — Developer experience

**Goal:** Make MyKOS a productive development workstation without prescribing one stack.

Work:
- Document supported developer setup patterns.
- Integrate access to terminal, Git, editors/IDEs, SDKs, runtimes, and container tooling.
- Consider a Developer Center only after requirements are validated.
- Test common workflows on a clean installation.

Acceptance:
- A developer can set up and run at least one documented representative workflow.
- Tool installation and environment setup are repeatable.
- Developer tooling does not compromise base OS integrity.

## M5 — Reliability and recovery

**Goal:** Make updates and recovery understandable and testable.

Work:
- Define update channels and release cadence.
- Implement clear update status and release notes.
- Test interrupted and failed updates.
- Evaluate filesystem snapshots and rollback integration.
- Document backup, recovery, and diagnostic procedures.
- Establish security update and vulnerability response practices.

Acceptance:
- Update behavior is tested on supported installation layouts.
- Recovery procedures are documented and exercised.
- Snapshot rollback, if enabled, is tested end-to-end and not represented as a backup.

## M6 — Public release 1.0

**Goal:** Publish a stable, supportable MyKOS release.

Work:
- Freeze the supported hardware matrix.
- Complete installation, desktop, update, recovery, and security testing.
- Publish release notes, known issues, checksums, and installation instructions.
- Document support channels and contribution guidelines.
- Tag the release and archive build metadata.

Acceptance:
- No unresolved release-blocking defects.
- Installation and update tests pass on the release matrix.
- Release artifacts are reproducible and verifiable.
- Documentation accurately describes supported hardware and limitations.

## Cross-cutting requirements

Every milestone should include:
- Documentation updates.
- Automated tests where practical.
- Accessibility and usability review.
- Security and permission review.
- Upstream compatibility review.
- Clear ownership and acceptance criteria.

## Explicitly deferred

Until there is evidence and capacity to maintain them, defer:
- A custom Linux kernel.
- A complete fork of KDE Plasma.
- A proprietary package format.
- A custom init system or replacement for core Linux services.
- Universal Windows application compatibility promises.
- Cloud account and cross-device synchronization.
- An immutable/image-based OS migration.

## Immediate next actions

1. Inspect and pin the selected Ubuntu LTS release.
2. Choose the ISO build toolchain and document why.
3. Create the smallest package manifest that produces a bootable KDE image.
4. Add a repeatable build script and QEMU smoke-test instructions.
5. Produce and test the first ISO before expanding the feature set.
