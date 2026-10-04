import { createContext } from "react";
import type { AppStore } from "./store";
// Keep the context identity outside the refreshable provider module.
export const Context = createContext<AppStore | null>(null);
