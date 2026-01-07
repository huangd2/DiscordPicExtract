# GitHub Repository Setup

## Step 1: Create the Repository on GitHub

1. Go to [GitHub](https://github.com) and sign in
2. Click the "+" icon in the top right corner
3. Select "New repository"
4. Name it: `DiscordPicExtract`
5. Choose public or private
6. **DO NOT** initialize with README, .gitignore, or license (we already have these)
7. Click "Create repository"

## Step 2: Connect Your Local Repository

After creating the repository on GitHub, run these commands in your terminal:

```bash
cd "C:\Users\Vivian\Desktop\DiscordPicExtract"
git remote add origin https://github.com/YOUR_USERNAME/DiscordPicExtract.git
git branch -M main
git push -u origin main
```

**Replace `YOUR_USERNAME` with your actual GitHub username.**

## Alternative: Using SSH

If you prefer SSH (and have SSH keys set up):

```bash
git remote add origin git@github.com:YOUR_USERNAME/DiscordPicExtract.git
git branch -M main
git push -u origin main
```

