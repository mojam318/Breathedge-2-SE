# Publish this source repository

The files in this folder are committed locally and ready to push to a public GitHub repository. A public URL is only useful to Nexus Support after the code and build instructions are visible there.

## Push to the supplied repository

The current local Git repository already has the initial source commit and the remote `https://github.com/mojam318/Breathedge-2-SE.git` configured. Once GitHub restores write access to that account, run from PowerShell:

```powershell
git push -u origin main
```

## Use another public repository

If the supplied GitHub account remains unavailable, create a new **Public** empty repository under an account with write access. In this folder, change the remote and push the prepared commit:

```powershell
git remote set-url origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```

Replace both placeholders with the new account and repository names. Open the resulting repository URL in a private browser window to confirm that it is publicly readable, then use that URL in the reply to Nexus Support.

This creates an initial source snapshot; it does not create historical development records. Because the code was produced substantially with generative AI, use Nexus Mods' **AI-Generated Content** tag rather than presenting it as AI-assisted human-led code.
