using System;
using System.IO;

namespace VectorMcpServer.Configuration;

public static class DotEnv
{
    public static void Load(params string[] paths)
    {
        if (paths == null)
        {
            return;
        }

        foreach (var path in paths)
        {
            if (string.IsNullOrWhiteSpace(path) || !File.Exists(path))
            {
                continue;
            }

            foreach (var line in File.ReadLines(path))
            {
                var trimmed = line.Trim();
                if (string.IsNullOrEmpty(trimmed) || trimmed.StartsWith('#'))
                {
                    continue;
                }

                var separatorIndex = trimmed.IndexOf('=');
                if (separatorIndex <= 0)
                {
                    continue;
                }

                var key = trimmed.Substring(0, separatorIndex).Trim();
                var value = trimmed.Substring(separatorIndex + 1).Trim();

                if (value.Length >= 2 && value.StartsWith('"') && value.EndsWith('"'))
                {
                    value = value.Substring(1, value.Length - 2);
                }

                if (string.IsNullOrWhiteSpace(key) || Environment.GetEnvironmentVariable(key) != null)
                {
                    continue;
                }

                Environment.SetEnvironmentVariable(key, value);
            }
        }
    }
}
