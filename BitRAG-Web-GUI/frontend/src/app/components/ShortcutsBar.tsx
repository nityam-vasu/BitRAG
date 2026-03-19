export function ShortcutsBar() {
  const shortcuts = [
    { key: 'C', label: 'Chat' },
    { key: 'S', label: 'Settings' },
    { key: 'U', label: 'Upload' },
  ];

  return (
    <footer className="border-t border-gray-200 dark:border-gray-800 bg-gray-100 dark:bg-[#0a0a0a] px-6 py-2">
      <div className="flex items-center gap-6 text-xs font-mono text-gray-500 dark:text-gray-600">
        {shortcuts.map((shortcut) => (
          <span key={shortcut.key}>
            <kbd className="px-2 py-1 bg-gray-200 dark:bg-gray-900 border border-gray-300 dark:border-gray-800 rounded text-gray-600 dark:text-gray-400">
              {shortcut.key}
            </kbd>{' '}
            → {shortcut.label}
          </span>
        ))}
      </div>
    </footer>
  );
}