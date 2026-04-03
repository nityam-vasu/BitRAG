# Simple commands to run the downloaded frontend

# 1. Copy downloaded frontend to project
cp -r /home/itsb2sinha/Downloads/mybatop/BitRAG/frontend/* /mnt/ed624ec7-962a-4a2a-95ca-e887f1cd9c96/Personal_Project/bitrag/Github_Latest/BitRAG/frontend/

# 2. Fix asset paths (remove leading /)
cd /mnt/ed624ec7-962a-4a2a-95ca-e887f1cd9c96/Personal_Project/bitrag/Github_Latest/BitRAG/frontend
sed -i 's|src="/assets/|src="assets/|g' index.html
sed -i 's|href="/assets/|href="assets/|g' index.html

# 3. Serve with Python (any of these)
# Option A: Python built-in
python3 -m http.server 5000

# Option B: Using npx serve
npx serve -p 5000

# Option C: Using PHP
php -S localhost:5000