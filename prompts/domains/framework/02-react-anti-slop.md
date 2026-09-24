-
id: 02-react-anti-slop
title: "React Anti-Slop Layer"
lang: en
depends_on: [00-master-anti-slop, 02-architecture-anti-slop]
category: domain
domain_type: framework
version: 1
---

# React Anti-Slop Layer

Layered under `_universal/00-master-anti-slop.md` and
`domains/framework/02-architecture-anti-slop.md`. Universal rules
(fabrication, fake completion, over-engineering, silent assumptions,
security anti-patterns, output format) and architectural rules
(layering, dependency direction, folder structure, naming) are NOT
repeated here.

This file covers rules specific to React: components, hooks, rendering,
lists, context, and the common patterns that cause unnecessary renders
or hidden coupling. General frontend rules (state management, data
fetching, forms, routing, effects) live in
`domains/delivery/02-frontend-anti-slop.md` and its siblings
(`02-state-anti-slop.md`, `02-api-data-anti-slop.md`). Framework meta-
layers (Next.js, Remix) add their own rules on top of this file.

## 1. Stack Assumptions

This layer assumes:

- React 18 or later. If the project uses React 17, concurrent features
  (`useTransition`, `useDeferredValue`, `useId`) and automatic batching
  are unavailable.
- Function components with hooks. Class components may exist in legacy
  code but are not written new.
- The project has a build setup (Vite, Next.js, CRA, Remix). This file
  does not assume any specific one.

If the project uses class components in active code, match the existing
style inside those files. Do not convert class to function while
working on unrelated tasks.

## 2. Component Discipline

### 2.1 Reference Before Creating

Before writing a new component:

1. Search the project's component folders for a similar component.
2. If something similar exists, use it.
3. If it is close but imperfect, report the gap and ask before
   replacing it.
4. Only create a new component when nothing close exists.

A duplicated `<Button>` is not a style preference. It is a future
inconsistency.

### 2.2 One Component Per File

Unless the project's pattern explicitly colocates sub-components, one
exported component per file. Small private helpers (a `Row` used only
by `Table`) may live in the same file.

### 2.3 Function Components Over Class Components

New components are function components. Never introduce a new class
component.

Class components are acceptable only when:

- The project's codebase is class-based and a new component must
  integrate with that pattern, or
- An error boundary is needed and the project has no `react-error-boundary`
  dependency.

### 2.4 Props Are Contracts

- Define props with an explicit type (`interface Props` or
  `type Props`).
- Never use `any` for props.
- Optional props have a documented default.
- Never spread unknown props with `...rest` unless forwarding to a DOM
  element (and then type the rest as `React.HTMLAttributes<...>` or the
  specific element's attributes).

### 2.5 Children Over Configuration Props

BAD:
tsx
<Card
  title="User"
  subtitle="Details"
  footerText="Save"
  onFooterClick={handleSave}
/>
GOOD:

tsx
<Card>
  <Card.Header>User</Card.Header>
  <Card.Body>Details</Card.Body>
  <Card.Footer>
    <Button onClick={handleSave}>Save</Button>
  </Card.Footer>
</Card>
Boolean props that toggle layout fragments turn a component into a
configuration language. Prefer composition.

2.6 Prop Drilling Beyond Two Levels
If a prop passes through more than two components unchanged, use the
project's context or store. Do not add a new pattern.

2.7 Component Size
A component over 150 lines is usually doing more than one thing.
Split only when each part has an independent responsibility. Do not
split to reduce line count.

2.8 File and Component Names Match
UserCard.tsx exports UserCard. Do not name the file
user-card.tsx and the component Card, or vice versa. Match the
project's convention.

3. Hooks
3.1 Rules of Hooks Are Absolute
Call hooks only at the top level of a component or another hook.

Never call hooks inside loops, conditions, or nested functions.

Never call hooks from regular JavaScript functions (only from
components and custom hooks).

Custom hooks start with use.

The ESLint rule react-hooks/rules-of-hooks enforces this. Never
disable it.

3.2 Dependencies Are Complete
useEffect, useMemo, useCallback, useLayoutEffect dependencies
must list every reactive value used inside the callback. Never suppress
react-hooks/exhaustive-deps without a comment that explains why.

If a dependency causes an infinite loop, the fix is to change the
logic, not to remove the dependency.

3.3 Do Not Derive State in an Effect
BAD:

tsx
const [fullName, setFullName] = useState("");
useEffect(() => {
  setFullName(`${first} ${last}`);
}, [first, last]);
GOOD:

tsx
const fullName = `${first} ${last}`;
3.4 Do Not Store Computable Values in State
BAD:

tsx
const [double, setDouble] = useState(count * 2);
GOOD:

tsx
const double = count * 2;
3.5 Do Not Memoize Before Measuring
useMemo and useCallback are performance tools, not correctness
tools. Add them only after profiling shows a real problem.

The default is: no useMemo, no useCallback. Add when there is a
specific reason:

A child is wrapped in React.memo and its props would change every
render.

The computation is genuinely expensive (sorting thousands of items,
building a large tree).

A value is a dependency of a hook whose identity matters.

3.6 Do Not Use useMemo for Correctness
If the value must be stable for correctness (not just performance),
that is a design smell. Reconsider the data flow rather than reaching
for useMemo.

3.7 Custom Hooks Extract Behavior, Not State Shape
A custom hook:

Encapsulates a reusable behavior or a data source.

Is used in two or more components, or has complex logic that
deserves a name.

A hook used in one component with five lines of logic does not earn
its own file. Keep it inline.

3.8 useRef for Mutable Values and DOM
useRef is for:

Holding a mutable value that does not trigger re-render (timer IDs,
previous values).

Direct DOM access for focus, scroll, or integrating a non-React
library.

Never useRef for something that should trigger a re-render. That is
useState.

3.9 useLayoutEffect Only When Required
useLayoutEffect runs synchronously before paint. It is needed only
when measuring the DOM and applying a fix before the user sees the
result. In all other cases, useEffect is correct.

Server-side rendering warns on useLayoutEffect. In SSR contexts, use
useIsomorphicLayoutEffect or the project's equivalent.

3.10 useTransition and useDeferredValue
For long lists and heavy renders, useTransition (on the state update)
and useDeferredValue (on a value) let React keep the UI responsive.
Use them when the project already uses them or when a real problem
exists, not as a default.

4. Rendering
4.1 Never Call setState During Render
BAD:

tsx
function Component() {
  const [count, setCount] = useState(0);
  if (count < 10) setCount(10); // infinite loop risk
  return <div>{count}</div>;
}
setState during render is allowed only in the specific "adjusting
state when props change" pattern with a conditional guard. If you are
not certain that is what you are doing, do not do it.

4.2 Never Mutate State Directly
BAD:

tsx
const [items, setItems] = useState([]);
items.push(newItem); // mutation, no re-render
GOOD:

tsx
const [items, setItems] = useState([]);
setItems(prev => [...prev, newItem]);
4.3 Batch State Updates
React 18 batches all state updates by default, including in promises,
timeouts, and native event handlers. Do not split a logically atomic
update into multiple setState calls expecting them to be sequential.

4.4 Functional Updates When Depending on Previous State
BAD:

tsx
setCount(count + 1);
If the update depends on the previous value, use the functional form:

tsx
setCount(c => c + 1);
4.5 Keys Must Be Stable
BAD:

tsx
{items.map((item, index) => <Row key={index} />)}
GOOD:

tsx
{items.map(item => <Row key={item.id} />)}
Index as key is acceptable only when the list is static (never
reorders, never inserts, never removes from the middle).

4.6 Never Render a Component Definition Inside Another Component
BAD:

tsx
function Parent() {
  function Child() { return <div />; }
  return <Child />;
}
Every render of Parent creates a new Child function. React unmounts
and remounts on every render, losing state and focus.

Define Child outside Parent, or inline its JSX.

4.7 Conditional Rendering
Use && or ternary for inline conditions. Never rely on falsy numeric
values accidentally rendering:

BAD:

tsx
{items.length && <List items={items} />} // renders "0" when empty
GOOD:

tsx
{items.length > 0 && <List items={items} />}
4.8 Suspense and Lazy
React.lazy and Suspense are for code-split routes and heavy
components. Do not lazy-load a 10-line component; the network round
trip costs more than the code saves.

5. Context
5.1 Context for Rare, Global Values
Context is for:

Theme

Locale / language

Auth session (when the project does not use a store for it)

Configuration that never changes during a session

Everything else belongs in props or the project's state manager.

5.2 Never Context for Frequently Changing Values
A context value that changes on every keystroke re-renders every
consumer. Use a store with selectors instead.

5.3 Context Value Is Memoized
BAD:

tsx
<AuthContext.Provider value={{ user, login, logout }}>
The object literal creates a new value every render, re-rendering all
consumers.

GOOD:

tsx
const value = useMemo(() => ({ user, login, logout }), [user, login, logout]);
<AuthContext.Provider value={value}>
Or split into multiple contexts so unrelated values do not share a
re-render boundary.

5.4 Custom Hook Over Raw Context
Export a useAuth() hook instead of the raw context. The hook can
throw a clear error when used outside the provider, which the raw
context cannot.

6. Lists and Keys
6.1 Stable Keys
Covered in 4.5. Repeating because it is the most common React warning.

6.2 Key Must Be on the Outermost Element in a Map
BAD:

tsx
{items.map(item => <li><Row key={item.id} item={item} /></li>)}
GOOD:

tsx
{items.map(item => <li key={item.id}><Row item={item} /></li>)}
The key belongs to the element that is repeated.

6.3 Never Fabricate a Key
key={Math.random()} or key={Date.now()} defeats reconciliation.
Every list item must have an inherent identifier.

6.4 Virtualize Only Large Lists
Virtualization is for 100+ items with complex rows. A 20-item list
does not need react-window.

7. Effects
7.1 Effects Are for Synchronization, Not Data Flow
An effect synchronizes React with an external system: DOM APIs, network
subscriptions, third-party widgets, timers. It is not the place to
transform data, derive values, or coordinate between siblings.

7.2 Fetching Belongs in the Data Layer
Covered in domains/delivery/02-frontend-anti-slop.md and
02-api-data-anti-slop.md. Repeating: useEffect is not the place
for raw fetch. Use the project's data-fetching library.

7.3 Every Effect Cleans Up
If the effect subscribes to anything (event listener, timer,
WebSocket, IntersectionObserver, ResizeObserver), the cleanup function
unsubscribes:

tsx
useEffect(() => {
  const onResize = () => setWidth(window.innerWidth);
  window.addEventListener("resize", onResize);
  return () => window.removeEventListener("resize", onResize);
}, []);
7.4 Effects Run Twice in Strict Mode
React Strict Mode double-invokes effects in development to catch
missing cleanup. An effect that breaks under double-invocation is
broken. Do not disable Strict Mode to make it pass.

7.5 Do Not Use an Effect to React to a State Change You Caused
BAD:

tsx
const [submitted, setSubmitted] = useState(false);
useEffect(() => {
  if (submitted) { navigate("/done"); }
}, [submitted]);
GOOD:

tsx
function handleSubmit() {
  // ...
  navigate("/done");
}
If you control the cause, act at the cause, not in an effect.

8. React-Specific Anti-Patterns
8.1 Conditional Hooks
Covered in 3.1. Repeating because it produces the most confusing bugs.

8.2 The useEffect Dependency Lie
Adding // eslint-disable-next-line react-hooks/exhaustive-deps without
a comment. The dependency is missing for a reason; make the reason
visible, or fix the dependency.

8.3 useState for Everything
Not every value is state. Values that come from props, URL, context,
or a store are not state. Values that can be derived are not state.

8.4 Prop Drilling Through children
Passing props to a deeply nested child by cloning its elements
(React.cloneElement) or by walking children. Both are anti-patterns.
Use context or restructure.

8.5 Rendering a Function That Returns JSX
BAD:

tsx
function Parent() {
  const renderRow = (item) => <Row item={item} />;
  return <div>{items.map(renderRow)}</div>;
}
This is acceptable when the function is defined outside the component
or memoized. Inside the component body without memoization, it creates
a new function on every render, which affects React.memo children.

For a plain list of <Row>, inline the JSX.

8.6 defaultProps on Function Components
defaultProps on function components is deprecated in React 18. Use
default parameter values in destructuring:

BAD:

tsx
Button.defaultProps = { size: "md" };
GOOD:

tsx
function Button({ size = "md", ...rest }) { /* ... */ }
8.7 propTypes in TypeScript Projects
propTypes duplicates what TypeScript checks at compile time. Use one
or the other, not both. In a TypeScript project, use TypeScript.

8.8 React.FC and Its Implicit children
React.FC (or React.FunctionComponent) implicitly added children
to props in older React versions. Modern code uses explicit props
without React.FC:

BAD:

tsx
const Card: React.FC<Props> = ({ title }) => ( /* children allowed but not typed */ );
GOOD:

tsx
function Card({ title, children }: PropsWithChildren<{ title: string }>) { /* ... */ }
8.9 Inline Object Props to Memoized Children
BAD:

tsx
<MemoChild style={{ color: "red" }} />
The object literal is new every render, defeating React.memo.

GOOD: Hoist the object outside the component, or accept the cost
knowingly.

8.10 setState Inside a Loop
BAD:

tsx
for (const item of items) {
  setCount(c => c + 1); // many re-renders
}
GOOD:

tsx
setCount(c => c + items.length);
8.11 Effects That Fetch on Every Render
BAD:

tsx
useEffect(() => { fetchData(); }); // no dependency array
Runs after every render, producing an infinite loop in most cases.

8.12 Layout Effects for Data
useLayoutEffect for fetching is a mistake. It blocks paint. Data
fetching belongs in the data layer, not in a layout effect.

8.13 Uncontrolled to Controlled Input Switch
BAD:

tsx
<input value={value} />
When value starts as undefined, React treats the input as
uncontrolled, then switches to controlled. Always pass a defined
initial value.

8.14 Missing key on Fragments in Lists
When a list item is a fragment (<>...</>), it cannot carry a key
directly. Use <React.Fragment key={...}>.

8.15 Callback Refs Without Cleanup
Callback refs that attach listeners or create objects must return a
cleanup function in React 19, or handle cleanup via the effect
pattern. In React 18 and earlier, the callback is called with null
on unmount; ensure the handler checks for null.

9. Response to Violation
If a previous response violated a rule here:

text
In the previous response, [specific rule] was violated. Correction:
[corrected code]
No justification. No apology paragraph. Fix and move on.



---